!-----------------------------------------------------------------------------------!
! Read in NetCDF file containing liquid water path and cluster clouds               !
!                                                                                   !
!  ftn -O3 -c -o clustering_cray.o clustering_periodic.f90                          !
!                                                                                   !
! ftn -target-network=none -O3 -o cloud_cluster cloud_cluster.f90 clustering_cray.o !
! `/opt/cray/pe/netcdf/4.4.1.1.3/bin/nf-config --fflags --flibs`                           !
!                                                                                   !
! ./cloud_cluster test.nc test2.nc                                                  !
!                                                                                   !
!-----------------------------------------------------------------------------------!
! Created by Linda Schlemmer                                                        !
!-----------------------------------------------------------------------------------!
! Modifications:                                                                    !
! 2017.12. - 2018.01. Christoph Heim (CH2017)                                       !
!       Adjust script to work with COSMO model output given at constant altitude    !
!       levels. Variables are given at altitude levels (no vertical staggering)     !
!       Major modifications are done in the script lwp.f90. Only few changes here.  !
!       Note 1: Resolution of model [km] is given by 3rd input argument.            !
!       Note 2: Adjustments only take into account a non-periodic domain            !
!       Note 3: For a non-periodic domain use                                       !
!               function file 'clustering_nonperiodic.f90'.                         !
!               Replace first compilation step with:                                ! 
!               ftn -O3 -c -o clustering_cray.o clustering_nonperiodic.f90          ! 
!-----------------------------------------------------------------------------------!


Program cloud_cluster

  use netcdf
  
  implicit none     
  
  !integer nx, ny, nz, nz2, nt
  integer nx, ny, nz, nt !CH2017: only full altitude levels

  character*80 infile,outfile, cstfile

  real, allocatable :: &
           
       lwp_in   (:,:,:),    & ! 
       lwp_ad_in(:,:,:),    & ! 
       base     (:,:,:),    & ! 
       top      (:,:,:),    & ! 
       mask     (:,:),      & ! 
       mf       (:,:,:),    & ! 
       wm       (:,:,:),    & ! 
       dqvsdz   (:,:,:),    & ! 
       qvs_cb   (:,:,:),    & ! 
       t_cb     (:,:,:),    & ! 
       out      (:,:,:)
  
  logical, allocatable :: &
   
       maskl    (:,:),    & !
       maskl2   (:,:),    & !
       maskl3   (:,:)

  real, allocatable :: &
       
       rlat   (:),    & ! 
       rlon   (:),    & ! 
       time   (:)

  integer, allocatable :: & ! cloud cluster properties

       nc   (:),      & ! number of clouds
       sc   (:,:),    & ! size of clouds
       ccb  (:,:),    & ! cloud base of cluster
       cct  (:,:)       ! cloud top of cluster

  real, allocatable :: &

       cmf  (:,:),    & ! cloud mean vertical velocity, density weighted
       cwm  (:,:),    & ! cloud mean vertical velocity
       dqvsm(:,:),    & ! mean vertical gradient of qvs
       qvsm (:,:),    & ! cloud base mean saturation specific humidity
       tm   (:,:),    & ! cloud base mean temperature
       ad   (:,:)       ! adiabaticness of cloud

  real, allocatable :: &

       dist_nearest (:,:),  & ! distance to nearest neighbour
       xcenter (:,:),       & ! x center of mass
       ycenter (:,:)          ! y center of mass

  
  real, allocatable :: bounds(:,:)

  !* netCDF id
  integer  ncid, ncido, status
  !* dimension ids
  integer londim, latdim, timedim, bndsdim, cdim
  !* variable ids
  integer timeid, tbid, rotpol, lonid, latid, cid
  integer varid, outid, nid, sid, cbid, ctid, wmid, mfid, dqvsmid, qvsmid, tmid, adid, xceid, yceid, dnnid

  integer i, j, k, t, m, n, iret, ind, ntot, nargs

  character(len=100) name

  integer maxt, maxc
  real, allocatable :: index(:)
  real :: icenter, jcenter, ianchor, janchor, idev, jdev, xrad, yrad, dist, dist1, dist2, dist3, dist4, dist_smallest, nxny2
  logical :: lcell
  character(len=10) :: resString ! CH2017: contains the resolution of the dataset in km.
  real :: res

  ! Read user input
  
  nargs = command_argument_count()
  if(nargs .ne. 3) then
     print*,'provide - input output - as arguments (see source code), STOPPING'
     stop
  else
     call get_command_argument(1,infile)
     call get_command_argument(2,outfile)
     call get_command_argument(3,resString)
     read(resString, *) res ! CH2017: Convert resolution in string to real.
  end if

  ! Open file
  
  status = nf90_open(infile, nf90_nowrite, ncid)
  IF (STATUS .NE. NF90_NOERR) THEN
     PRINT *, NF90_STRERROR(STATUS)
     STOP
  ENDIF
  
  ! inquire dimensions
  
  status=nf90_inquire(ncid,unlimitedDimID=timeid)
  status=nf90_inquire_dimension(ncid,timeid,len=nt)
  status=nf90_inq_dimid(ncid,"rlon",lonid)
  status=nf90_inquire_dimension(ncid,lonid,len=nx)
  status=nf90_inq_dimid(ncid,"rlat",latid)
  status=nf90_inquire_dimension(ncid,latid,len=ny)

  ! allocate fields

  allocate(lwp_in(nx,ny,nt))
  allocate(lwp_ad_in(nx,ny,nt))
  allocate(base(nx,ny,nt))
  allocate(top(nx,ny,nt))
  allocate(wm(nx,ny,nt))
  allocate(mf(nx,ny,nt))
  allocate(dqvsdz(nx,ny,nt))
  allocate(qvs_cb(nx,ny,nt))
  allocate(t_cb(nx,ny,nt))
  allocate(out(nx,ny,nt))
  allocate(mask(nx,ny))
  allocate(maskl(nx,ny))
  allocate(maskl2(nx,ny))
  allocate(maskl3(nx,ny))

  allocate(rlon(nx))
  allocate(rlat(ny))
  allocate(time(nt))
  allocate(bounds(2,nt))

  lwp_in(:,:,:)   = 0.0
  lwp_ad_in(:,:,:)= 0.0
  dqvsdz(:,:,:)   = 0.0
  qvs_cb(:,:,:)   = 0.0
  t_cb(:,:,:)     = 0.0
  mask(:,:)       = 0.0
  out(:,:,:)      = 0.0

  rlat(:)         = 0.0
  rlon(:)         = 0.0
  time(:)         = 0.0

  ! Read in variables
  
!  print*,'READING VARIABLES'

!  print*,'        TIME'

  status = nf90_inq_varid(ncid,"time", timeid)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_get_var(ncid,timeid,time)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
!  print*,'        BNDS'
  status = nf90_inq_varid(ncid,"time_bnds", tbid)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_get_var(ncid,tbid,bounds)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
!  print*,'        RLON'
  status = nf90_inq_varid(ncid,"rlon", lonid)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_get_var(ncid,lonid,rlon)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
!  print*,'        RLAT'
  status = nf90_inq_varid(ncid,"rlat", latid)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_get_var(ncid,latid,rlat)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
!  print*,'        LWP'
  status = nf90_inq_varid(ncid,"LWP", varid)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_get_var(ncid,varid,lwp_in)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
  status = nf90_inq_varid(ncid,"LWP_AD", varid)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_get_var(ncid,varid,lwp_ad_in)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
!  print*,'        BASE'
  status = nf90_inq_varid(ncid,"CB", varid)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_get_var(ncid,varid,base)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
!  print*,'        TOP'
  status = nf90_inq_varid(ncid,"CT", varid)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_get_var(ncid,varid,top)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
!  print*,'        MF'
  status = nf90_inq_varid(ncid,"MF", varid)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_get_var(ncid,varid,mf)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
!  print*,'        WM'
  status = nf90_inq_varid(ncid,"WM", varid)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_get_var(ncid,varid,wm)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
!  print*,'        DQVSDZ'
  status = nf90_inq_varid(ncid,"DQVSDZ", varid)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_get_var(ncid,varid,dqvsdz)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
!  print*,'        QVS_CB'
  status = nf90_inq_varid(ncid,"QVS_CB", varid)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_get_var(ncid,varid,qvs_cb)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
!  print*,'        T_CB'
  status = nf90_inq_varid(ncid,"T_CB", varid)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_get_var(ncid,varid,t_cb)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  

  ! Calculations

  do t=1,nt

!     do j=4,ny-3
!        do i=4,nx-3
!           if (lwp_in(i,j,t)>0.1) then
!              mask(i,j)=1
!           else
!              mask(i,j)=0
!           endif
!        enddo
!     enddo

     where(lwp_in(:,:,t) > 0.01) mask = 1.

     ntot=1

     !call clustering(out(:,:,t),ntot,mask,1.0,1.0,1.0,1.0,nx,ny)
     !              ! outar      ntot inar,xmin,ymin,dx,dy,nx,ny   
     ! CH2017: no fixed resolution, instead use 'res' given by user input.
     !         'res' input is not used by clustering_nonperiodic.f90.
     !         I decided to keep it in case somebody wants to us clustering_periodic.f90
     !         for cases with varying model resolution.
     call clustering(out(:,:,t),ntot,mask,res,res,res,res,nx,ny)
                   ! outar      ntot inar,xmin,ymin,dx,dy,nx,ny   

  end do

  maxc = max(1,int(maxval(out)))

  allocate(nc(nt))
  allocate(sc(maxc,nt))
  allocate(ccb(maxc,nt))
  allocate(cct(maxc,nt))
  allocate(cmf(maxc,nt))
  allocate(cwm(maxc,nt))
  allocate(qvsm(maxc,nt))
  allocate(dqvsm(maxc,nt))
  allocate(tm(maxc,nt))
  allocate(ad(maxc,nt))
  allocate(index(maxc))
  allocate(xcenter(maxc,nt))
  allocate(ycenter(maxc,nt))
  allocate(dist_nearest(maxc,nt))

  nc(:)    = 0
  sc(:,:)  = 0
  ccb(:,:) = 0
  cct(:,:) = 0
  cmf(:,:) = 0
  cwm(:,:) = 0
  dqvsm(:,:)  = -999.
  qvsm(:,:)   = -999.
  tm(:,:)     = -999.
  ad(:,:)     = -999.

  xcenter(:,:)      = -999.
  ycenter(:,:)      = -999.
  dist_nearest(:,:) = -999.

  index = (/(i, i=1,maxc,1)/)
  if (maxc==1) index = 0

  nxny2 = sqrt(real(nx)**2+real(ny)**2) ! TODO ?

  do t=1,nt

     maxt = int(maxval(out(:,:,t)))
     nc(t) = maxt

     if (maxt.gt.0) then

        do m = 1,maxt ! loop over clusters

           mask(:,:)   = 0.
           maskl(:,:)  = .False.
           maskl2(:,:) = .False.
           maskl3(:,:) = .False.

           where(out(:,:,t)==m) mask = 1
           where(out(:,:,t)==m) maskl = .True.
           where((out(:,:,t)==m).and.(base(:,:,t).ne.-999.)) maskl2 = .True.
           where((out(:,:,t)==m).and.(mf(:,:,t).gt.0.)) maskl3 = .True. ! cloudy updraft

           sc(m,t)    = int(sum(mask))
           ccb(m,t)   = minval(base(:,:,t),maskl) ! lowest cloud base found in the cloud
           cct(m,t)   = maxval(top(:,:,t),maskl) ! highest cloud top found in the cloud
           ! lowest cloud base found in the cloud
           cmf(m,t)   = sum(mf(:,:,t),maskl3)/max(1,count(maskl3)) 
           if (count(maskl3)==0) cmf(m,t) = -999. ! set to missing value if cloud has no base
           ! highest cloud top found in the cloud
           cwm(m,t)   = sum(wm(:,:,t),maskl2)/max(1,count(maskl2)) 
           ! mean vertical qvs gradient
           dqvsm(m,t) = sum(dqvsdz(:,:,t),maskl3)/max(1,count(maskl3)) 
           ! set to missing value if cloud has no base
           if (count(maskl3)==0) dqvsm(m,t) = -999. 
           ! mean saturation specific humidity
           qvsm(m,t)  = sum(qvs_cb(:,:,t),maskl2)/max(1,count(maskl2)) 
           ! set to missing value if cloud has no base
           if (count(maskl2)==0) qvsm(m,t)  = -999. 
           tm(m,t)   = sum(t_cb(:,:,t),maskl2)/max(1,count(maskl2)) ! mean temperature
           if (count(maskl2)==0) tm(m,t) = -999. ! set to missing value if cloud has no base
           ! mean ratio of lwp to lwp_ad
           ad(m,t)   = sum(lwp_in(:,:,t)/lwp_ad_in(:,:,t),maskl2)/max(1,count(maskl2))
           if (count(maskl2)==0) ad(m,t) = -999. ! set to missing value if cloud has no base

           ! find center of cloud
           ! periodic domain, and some clouds are distributed across the edge. 
           ! Thus, an anchor is defined and the points relative to the anchor are taken
           !
           ! CH2017: no periodic domain for my case.

           icenter=0.
           jcenter=0.
           ianchor=0.
           janchor=0.
           lcell = .false.

           xrad = real(nx)*3./4!-2.*sqrt(sum(mask))
           yrad = real(ny)*3./4!-2.*sqrt(sum(mask))

           !do j=4,ny-3
           !   do i=4,nx-3
           ! CH2017: no periodic domain --> loop from lowest to highest index in horizontal.
           do j=1,ny
              do i=1,nx
                 if (out(i,j,t)==m) then
                    ! the first point of the cell found is its anchor
                    if (.not.lcell) then
                       ianchor = real(i)
                       janchor = real(j)
                       lcell = .true.
                    end if
                    idev = real(i)-ianchor
                    jdev = real(j)-janchor
                    ! CH2017: Periodic part ignored. 
                    !if(abs(idev).gt.xrad) idev=-sign(real(nx)-6.,idev)+idev
                    !if(abs(jdev).gt.yrad) jdev=-sign(real(ny)-6.,jdev)+jdev
                    icenter = icenter + idev
                    jcenter = jcenter + jdev

                 end if
              end do
           end do

           icenter = icenter/sum(mask)
           jcenter = jcenter/sum(mask)

           xcenter(m,t) = icenter + ianchor
           ycenter(m,t) = jcenter + janchor
           
           ! FOR PERIODIC DOMAIN
           ! CH2017: no periodic domain.
           !if (xcenter(m,t).gt.(real(nx)-3.)) xcenter(m,t) = xcenter(m,t) -real(nx) + 6.
           !if (ycenter(m,t).gt.(real(ny)-3.)) ycenter(m,t) = ycenter(m,t) -real(ny) + 6.
           !if (xcenter(m,t).lt.(4.)) xcenter(m,t) = xcenter(m,t) +real(nx) - 6.
           !if (ycenter(m,t).lt.(4.)) ycenter(m,t) = ycenter(m,t) +real(ny) - 6.
        end do
        ! determine nearest-neighbour distance
        do m = 1,maxt ! loop over clusters
           dist_smallest = nxny2
           do n = 1,maxt ! loop over the other clusters
              if (n.ne.m) then
                 ! PERIODIC SOLUTION
                 ! the domain is periodic, thus we need to check for the "direct"
                 ! distance and the one 
                 ! across the borders
                 !dist1 = sqrt((xcenter(m,t)-xcenter(n,t))**2&
                 !       +(ycenter(m,t)-ycenter(n,t))**2)
                 !dist2 = sqrt((xcenter(m,t)-xcenter(n,t)+real(nx)-6.)**2&
                 !       +(ycenter(m,t)-ycenter(n,t))**2)
                 !dist3 = sqrt((xcenter(m,t)-xcenter(n,t))**2&
                 !       +(ycenter(m,t)-ycenter(n,t)+real(ny)-6.)**2)
                 !dist4 = sqrt((xcenter(m,t)-xcenter(n,t)+real(nx)-6.)**2&
                 !       +(ycenter(m,t)-ycenter(n,t)+real(ny)-6.)**2)
                 !dist = min(dist1,dist2,dist3,dist4)

                 ! CH2017: NONE-PERIODIC SOLUTION
                 dist = sqrt((xcenter(m,t)-xcenter(n,t))**2&
                        +(ycenter(m,t)-ycenter(n,t))**2)

                 if (dist.lt.dist_smallest) dist_smallest=dist
              end if
           end do
           dist_nearest(m,t) = dist_smallest
        end do
     end if

  end do


  ! write out results
  
  !print*,'CREATE NEW NetCDF FILE'

  !* enter define mode
  status = nf90_create (outfile,  NF90_CLOBBER, ncido)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
  
  !* define dimensions
  status = nf90_def_dim(ncido, 'time', nf90_unlimited,timedim)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_def_dim(ncido, 'bnds', 2, bndsdim)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_def_dim(ncido, 'rlon', nx, londim)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_def_dim(ncido, 'rlat', ny, latdim)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  status = nf90_def_dim(ncido, 'cloud', maxc, cdim)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  !* define variables
  
  iret = nf90_def_var(ncido, 'time', NF90_FLOAT,(/timedim/), timeid)
  call check_err(iret)
  
  iret = nf90_def_var(ncido, 'time_bnds', NF90_FLOAT,(/bndsdim,timedim/), tbid)
  call check_err(iret)
  
  iret = nf90_def_var(ncido, 'rlon', NF90_FLOAT,(/londim/), lonid)
  call check_err(iret)
  
  iret = nf90_def_var(ncido, 'rlat', NF90_FLOAT,(/latdim/), latid)
  call check_err(iret)
  
  iret = nf90_def_var(ncido, 'cloud', NF90_FLOAT,(/cdim/), cid)
  call check_err(iret)

  iret = nf90_def_var(ncido, 'OUT', NF90_FLOAT,(/londim,latdim,timedim/),outid)
  call check_err(iret)

  iret = nf90_def_var(ncido, 'NC', NF90_FLOAT,(/timedim/),nid)
  call check_err(iret)

  iret = nf90_def_var(ncido, 'SC', NF90_FLOAT,(/cdim,timedim/),sid)
  call check_err(iret)

  iret = nf90_def_var(ncido, 'CB', NF90_FLOAT,(/cdim,timedim/),cbid)
  call check_err(iret)

  iret = nf90_def_var(ncido, 'CT', NF90_FLOAT,(/cdim,timedim/),ctid)
  call check_err(iret)

  iret = nf90_def_var(ncido, 'MF', NF90_FLOAT,(/cdim,timedim/),mfid)
  call check_err(iret)

  iret = nf90_def_var(ncido, 'WM', NF90_FLOAT,(/cdim,timedim/),wmid)
  call check_err(iret)

  iret = nf90_def_var(ncido, 'QVSM', NF90_FLOAT,(/cdim,timedim/),qvsmid)
  call check_err(iret)

  iret = nf90_def_var(ncido, 'DQVSM', NF90_FLOAT,(/cdim,timedim/),dqvsmid)
  call check_err(iret)

  iret = nf90_def_var(ncido, 'TM', NF90_FLOAT,(/cdim,timedim/),tmid)
  call check_err(iret)

  iret = nf90_def_var(ncido, 'AD', NF90_FLOAT,(/cdim,timedim/),adid)
  call check_err(iret)

  iret = nf90_def_var(ncido, 'XCENTER', NF90_FLOAT,(/cdim,timedim/),xceid)
  call check_err(iret)

  iret = nf90_def_var(ncido, 'YCENTER', NF90_FLOAT,(/cdim,timedim/),yceid)
  call check_err(iret)

  iret = nf90_def_var(ncido, 'DIST_NEAREST', NF90_FLOAT,(/cdim,timedim/),dnnid)
  call check_err(iret)

!  print*,'ATTRIBUTES'
  status = nf90_inq_varid(ncid,"time", varid)
  iret = nf90_get_att(ncid, varid,'standard_name',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, timeid,'standard_name',trim(name))
  call check_err(iret)
  iret = nf90_get_att(ncid, varid,'long_name',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, timeid,'long_name',trim(name))
  call check_err(iret)
  iret = nf90_get_att(ncid, varid,'units',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, timeid,'units',trim(name))
  call check_err(iret)
  iret = nf90_get_att(ncid, varid,'calendar',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, timeid,'calendar',trim(name))
  call check_err(iret)
  iret = nf90_get_att(ncid, varid,'bounds',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, timeid,'bounds',trim(name))
  call check_err(iret)

  status = nf90_inq_varid(ncid,"time_bnds", varid)
  iret = nf90_get_att(ncid, varid,'long_name',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, tbid,'long_name',trim(name))
  call check_err(iret)
  iret = nf90_get_att(ncid, varid,'units',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, tbid,'units',trim(name))
  call check_err(iret)

  status = nf90_inq_varid(ncid,"rlat", varid)
  iret = nf90_get_att(ncid, varid,'standard_name',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, latid,'standard_name',trim(name))
  call check_err(iret)
  iret = nf90_get_att(ncid, varid,'long_name',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, latid,'long_name',trim(name))
  call check_err(iret)
  iret = nf90_get_att(ncid, varid,'units',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, latid,'units',trim(name))
  call check_err(iret)

  status = nf90_inq_varid(ncid,"rlon", varid)
  iret = nf90_get_att(ncid, varid,'standard_name',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, lonid,'standard_name',trim(name))
  call check_err(iret)
  iret = nf90_get_att(ncid, varid,'long_name',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, lonid,'long_name',trim(name))
  call check_err(iret)
  iret = nf90_get_att(ncid, varid,'units',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, lonid,'units',trim(name))
  call check_err(iret)

  iret = nf90_put_att(ncido, cid,'standard_name','cloud number')
  call check_err(iret)
  iret = nf90_put_att(ncido, cid,'long_name','id of cloud cluster')
  call check_err(iret)
  iret = nf90_put_att(ncido, cid,'units','')
  call check_err(iret)

  status = nf90_inq_varid(ncid,"LWP", varid)
  iret = nf90_put_att(ncido, outid,'standard_name','clustered liquid water path')
  call check_err(iret)
  iret = nf90_put_att(ncido, outid,'long_name','clustered liquid water path')
  call check_err(iret)
  iret = nf90_put_att(ncido, outid,'units','')
  call check_err(iret)
  iret = nf90_get_att(ncid, varid,'grid_mapping',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, outid,'grid_mapping',trim(name))
  call check_err(iret)
  iret = nf90_get_att(ncid, varid,'coordinates',name)
  call check_err(iret)
  iret = nf90_put_att(ncido, outid,'coordinates',trim(name))
  call check_err(iret)

  iret = nf90_put_att(ncido, nid,'standard_name','number of clouds')
  call check_err(iret)
  iret = nf90_put_att(ncido, nid,'long_name','number of clouds')
  call check_err(iret)
  iret = nf90_put_att(ncido, nid,'units','')
  call check_err(iret)

  iret = nf90_put_att(ncido, sid,'standard_name','size of cloud cluster')
  call check_err(iret)
  iret = nf90_put_att(ncido, sid,'long_name','size of cloud cluster')
  call check_err(iret)
  iret = nf90_put_att(ncido, sid,'units','number points')
  call check_err(iret)

  iret = nf90_put_att(ncido, cbid,'standard_name','base of cloud cluster')
  call check_err(iret)
  iret = nf90_put_att(ncido, cbid,'long_name','base of cloud cluster')
  call check_err(iret)
  iret = nf90_put_att(ncido, cbid,'units','level')
  call check_err(iret)
  iret = nf90_put_att(ncido, cbid,'_FillValue',-999.)
  call check_err(iret)

  iret = nf90_put_att(ncido, ctid,'standard_name','top of cloud cluster')
  call check_err(iret)
  iret = nf90_put_att(ncido, ctid,'long_name','top of cloud cluster')
  call check_err(iret)
  iret = nf90_put_att(ncido, ctid,'units','level')
  call check_err(iret)
  iret = nf90_put_att(ncido, ctid,'_FillValue',-999.)
  call check_err(iret)

  iret = nf90_put_att(ncido, mfid,'standard_name','mean vertical velocity of cloud cluster')
  call check_err(iret)
  iret = nf90_put_att(ncido, mfid,'long_name','mean vertical velocity of cloud cluster, density weighted')
  call check_err(iret)
  iret = nf90_put_att(ncido, mfid,'units','m s-1')
  call check_err(iret)
  iret = nf90_put_att(ncido, mfid,'_FillValue',-999.)
  call check_err(iret)

  iret = nf90_put_att(ncido, wmid,'standard_name','mean vertical velocity of cloud cluster')
  call check_err(iret)
  iret = nf90_put_att(ncido, wmid,'long_name','mean vertical velocity of cloud cluster')
  call check_err(iret)
  iret = nf90_put_att(ncido, wmid,'units','m s-1')
  call check_err(iret)
  iret = nf90_put_att(ncido, wmid,'_FillValue',-999.)
  call check_err(iret)

  iret = nf90_put_att(ncido, dqvsmid,'standard_name','mean vertical gradient of saturation specific humidity')
  call check_err(iret)
  iret = nf90_put_att(ncido, dqvsmid,'long_name','mean vertical gradient of saturation specific humidity')
  call check_err(iret)
  iret = nf90_put_att(ncido, dqvsmid,'units','kg kg-1')
  call check_err(iret)
  iret = nf90_put_att(ncido, dqvsmid,'_FillValue',-999.)
  call check_err(iret)

  iret = nf90_put_att(ncido, qvsmid,'standard_name','mean saturation specific humidity at cloud base')
  call check_err(iret)
  iret = nf90_put_att(ncido, qvsmid,'long_name','mean saturation specific humidity at cloud base')
  call check_err(iret)
  iret = nf90_put_att(ncido, qvsmid,'units','kg kg-1')
  call check_err(iret)
  iret = nf90_put_att(ncido, qvsmid,'_FillValue',-999.)
  call check_err(iret)

  iret = nf90_put_att(ncido, tmid,'standard_name','mean temperature at cloud base')
  call check_err(iret)
  iret = nf90_put_att(ncido, tmid,'long_name','mean cloud base temperature')
  call check_err(iret)
  iret = nf90_put_att(ncido, tmid,'units','K')
  call check_err(iret)
  iret = nf90_put_att(ncido, tmid,'_FillValue',-999.)
  call check_err(iret)

  iret = nf90_put_att(ncido, adid,'standard_name','mean adiabaticness of cloud')
  call check_err(iret)
  iret = nf90_put_att(ncido, adid,'long_name','ratio of lwp to adiabatic lwp averaged over cloud')
  call check_err(iret)
  iret = nf90_put_att(ncido, adid,'units','')
  call check_err(iret)
  iret = nf90_put_att(ncido, adid,'_FillValue',-999.)
  call check_err(iret)

  iret = nf90_put_att(ncido, xceid,'standard_name','x center of cloud')
  call check_err(iret)
  iret = nf90_put_att(ncido, xceid,'long_name','x coordinate of center of cloud')
  call check_err(iret)
  iret = nf90_put_att(ncido, xceid,'units','')
  call check_err(iret)
  iret = nf90_put_att(ncido, xceid,'_FillValue',-999.)
  call check_err(iret)

  iret = nf90_put_att(ncido, yceid,'standard_name','y center of cloud')
  call check_err(iret)
  iret = nf90_put_att(ncido, yceid,'long_name','y coordinate of center of cloud')
  call check_err(iret)
  iret = nf90_put_att(ncido, yceid,'units','')
  call check_err(iret)
  iret = nf90_put_att(ncido, yceid,'_FillValue',-999.)
  call check_err(iret)

  iret = nf90_put_att(ncido, dnnid,'standard_name','distance to nearest neighbour')
  call check_err(iret)
  iret = nf90_put_att(ncido, dnnid,'long_name','distance to nearest neighbour cloud')
  call check_err(iret)
  iret = nf90_put_att(ncido, dnnid,'units','points')
  call check_err(iret)
  iret = nf90_put_att(ncido, dnnid,'_FillValue',-999.)
  call check_err(iret)

!* leave define mode
  STATUS = NF90_ENDDEF(ncido)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

!* store variables
!  print*,'STORE VARIABLES'
  STATUS = NF90_PUT_VAR(ncido, timeid,time)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, tbid,bounds)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
  STATUS = NF90_PUT_VAR(ncido, lonid, rlon)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
  STATUS = NF90_PUT_VAR(ncido, latid, rlat)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
  STATUS = NF90_PUT_VAR(ncido, cid, index)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, outid,out)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, nid,nc)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, sid,sc)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, cbid,ccb)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, ctid,cct)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, mfid,cmf)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, wmid,cwm)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, dqvsmid,dqvsm)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, qvsmid,qvsm)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, tmid,tm)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, adid,ad)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, xceid,xcenter)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, yceid,ycenter)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_PUT_VAR(ncido, dnnid,dist_nearest)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_CLOSE(ncido)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

  STATUS = NF90_CLOSE(NCID)
  IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
  
contains
  subroutine check_err(iret)

    use netcdf
    implicit none
    integer iret
    if (iret .ne. NF90_NOERR) then
       print *, nf90_strerror(iret)
       stop
    endif
  
  end subroutine check_err


end Program cloud_cluster
