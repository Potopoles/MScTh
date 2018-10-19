!-----------------------------------------------------------------------------------!
! Read in NetCDF file and calculate liquid water path                               !
!                                                                                   !
!                                                                                   !
! ftn -o lwp lwp.f90 `/opt/cray/pe/netcdf/4.4.1.1.3/bin/nf-config --fflags --flibs` !
!                                                                                   !
! ./lwp /scratch/pr04/heimc/01_rawData/4.4/lffd2006071515z.nc test.nc               !
!                                                                                   ! 
!                                                                                   !
!                                                                                   !
!-----------------------------------------------------------------------------------!
! Created by Linda Schlemmer                                                        !
!-----------------------------------------------------------------------------------!
! Modifications:                                                                    !
! 2017.12. - 2018.01. Christoph Heim (CH2017)                                       !
!       Adjust script to work with COSMO model output given at constant altitude    !
!       levels. Variables are given at altitude levels (no vertical staggering)     !
!       Vertical integration is performed over height instead of pressure.          !
!       Additionally, the given model output has nan values where topography is     !
!       present. The script was changed to account for nan values.                  !
!       NOTE: Altitude of model output levels are set manually within the           !
!             the script at line ~353                                               !
!-----------------------------------------------------------------------------------!

Program lwp

    use netcdf

    implicit none     

    !integer nx, ny, nz, nz2, nt   !CH2017: no vertical staggering for altitude levels
    integer nx, ny, nz, nt   !CH2017

    character*80 infile,outfile

    real, allocatable :: &

        p_in   (:,:,:,:),    & !
        t_in   (:,:,:,:),    & !
        qv_in  (:,:,:,:),    & !
        qc_in  (:,:,:,:),    & !
        qr_in  (:,:,:,:),    & !
        qi_in  (:,:,:,:),    & !
        qs_in  (:,:,:,:),    & !
        qg_in  (:,:,:,:),    & !
        !qh_in  (:,:,:,:),    & !   !CH2017: no hail
        w_in   (:,:,:,:),    & !
        qt_in   (:,:,:),     & ! sum of all hydrometeors (at the end of the script)
        qc_ad   (:,:,:),     & ! adiabatic qc

        wvp_out   (:,:,:),    & ! water vapour path
        lwp_out   (:,:,:),    & ! liquid water path
        lwp_ad_out(:,:,:),    & ! adiabatic liquid water path?
        iwp_out   (:,:,:),    & ! ice water path
        all_out   (:,:,:),    & ! all sort of water
        hyd_out   (:,:,:),    & ! all hydrometeors
        ! mean convective mass flux (mf = rho*sig*(1-sig)*(w_up - w_do)
        mf_out    (:,:,:),    & 
        wm_out    (:,:,:),    & ! mean vertical velocity
        dqvsdz    (:,:,:),    & ! vert. gradient of qvs (saturation specific humidity)
        qv_cb     (:,:,:),    & ! qv at cloud base
        qvs_cb    (:,:,:),    & ! qvs (saturation specific humidty) at cloud base
        p_cb      (:,:,:),    & ! pressure at cloud base
        t_cb      (:,:,:)       ! t at cloud base

    real, allocatable :: &

        cb_out    (:,:,:),    & ! cloud base
        ct_out    (:,:,:)       ! cloud top

    integer, allocatable  :: & ! integer of altitude level of cloud base

        cb_int    (:,:),    & ! cloud base
        ct_int    (:,:)       ! cloud top

    real, allocatable :: &

        t_inv   (:),    & ! temperature following moist adiabat
        qvs_inv (:)       ! qvs -"-

    real, allocatable :: &

        rlat   (:),    & !
        rlon   (:),    & !
        !zm     (:),    & ! half levels     !CH2017: no half levels
        zt     (:),    & ! full levels, from zm 
        time   (:)

    real, allocatable :: bounds(:,:) ! time_bnds

    !* netCDF id
    integer  ncid, ncido, status
    !* dimension ids
    integer londim, latdim, timedim, bndsdim, levdim
    !* variable ids
    integer timeid, tbid, rotpol, lonid, latid, levid
    integer varid, outlid, outlaid, outiid, outhid, outaid, outbid, outtid, outmfid, &
            outwmid, outdqid, outqvcbid, outqvscbid, outpcbid, outtcbid, outvid

    integer i, j, k, t, iret, ind, ntot, nargs, cb, ct, ctw

    character(len=100) name

    real     ::    &
        ztx,zpx,zgex,             &
        fesatw,                   & ! Function for equilibrium vapour pressure over water
        fqvs,                     & ! Function for saturation specific humidity
        esatp

    real :: dn, tv, wm, mf, mint, zint, wmm,  theta_es, qvs, qvscb, tmp, sum

    real*8  :: rt
    integer :: icountnew, icountold, icountrate, icountmax

    real, parameter :: Rd  = 287.04
    real, parameter :: Rm  = 461.5
    real, parameter :: ep2 = Rm/Rd - 1.
    real, parameter :: Rdv =  Rd / Rm
    real, parameter :: o_m_rdv  =  1.0 - Rdv 
    real, parameter :: b1  =  610.78
    real, parameter :: b2w =  17.2693882
    real, parameter :: b3  =  273.16
    real, parameter :: b4w =  35.86
    real, parameter :: p00 =  1.e5

    integer, parameter :: mdv = -999

    real test ! CH2017: debugging

    ! Calculation of saturation specific humidity and equivalent potential temperature, 
    ! based upon Bolton's approximations (1980), see also Emanuel (1994.)
    fesatw(ztx)     = b1*EXP( b2w*(ztx-b3)/(ztx-b4w) )   ! Sat.vap. pressure over water
    fqvs(zgex,zpx)  = rdv*zgex/( zpx - o_m_rdv*zgex )    ! Specific humidity at saturation

    CALL SYSTEM_CLOCK(COUNT=icountold,COUNT_RATE=icountrate,COUNT_MAX=icountmax)

    ! Read user input

    nargs = command_argument_count()
    if(nargs .ne. 2) then
     print*,'provide - input output - as arguments (see source code), STOPING'
     stop
    else
     call get_command_argument(1,infile)
     call get_command_argument(2,outfile)
    end if

    ! Open file

    status = nf90_open(infile, nf90_nowrite, ncid)
    IF (STATUS .NE. NF90_NOERR) THEN
     PRINT *, NF90_STRERROR(STATUS)
     STOP
    ENDIF

    ! inquire dimensions
    ! CH2017: adjusted to given model output
    status=nf90_inquire(ncid,unlimitedDimID=timeid)
    status=nf90_inquire_dimension(ncid,timeid,len=nt)
    status=nf90_inq_dimid(ncid,"rlon",lonid)
    status=nf90_inquire_dimension(ncid,lonid,len=nx)
    status=nf90_inq_dimid(ncid,"rlat",latid)
    status=nf90_inquire_dimension(ncid,latid,len=ny)
    status=nf90_inq_dimid(ncid,"altitude",levid)
    status=nf90_inquire_dimension(ncid,levid,len=nz)
    !status=nf90_inq_dimid(ncid,"level1",levid)
    !status=nf90_inquire_dimension(ncid,levid,len=nz2)

    ! allocate fields

    allocate(p_in(nx,ny,nz,nt))
    allocate(t_in(nx,ny,nz,nt))
    allocate(qv_in(nx,ny,nz,nt))
    allocate(qc_in(nx,ny,nz,nt))
    allocate(qr_in(nx,ny,nz,nt))
    allocate(qi_in(nx,ny,nz,nt))
    allocate(qs_in(nx,ny,nz,nt))
    allocate(qg_in(nx,ny,nz,nt))
    !allocate(qh_in(nx,ny,nz,nt))   !CH2017: no hail
    allocate(w_in(nx,ny,nz,nt))
    allocate(qt_in(nx,ny,nz))
    allocate(qc_ad(nx,ny,nz))
    allocate(wvp_out(nx,ny,nt))
    allocate(lwp_out(nx,ny,nt))
    allocate(lwp_ad_out(nx,ny,nt))
    allocate(iwp_out(nx,ny,nt))
    allocate(hyd_out(nx,ny,nt))
    allocate(all_out(nx,ny,nt))
    allocate(cb_out(nx,ny,nt))
    allocate(ct_out(nx,ny,nt))
    allocate(mf_out(nx,ny,nt))
    allocate(wm_out(nx,ny,nt))
    allocate(dqvsdz(nx,ny,nt))
    allocate(qv_cb(nx,ny,nt))
    allocate(qvs_cb(nx,ny,nt))
    allocate(p_cb(nx,ny,nt))
    allocate(t_cb(nx,ny,nt))

    allocate(cb_int(nx,ny))
    allocate(ct_int(nx,ny))

    allocate(t_inv(nz))
    allocate(qvs_inv(nz))

    allocate(rlon(nx))
    allocate(rlat(ny))
    !allocate(zm(nz2))      !CH2017: no vertical staggering
    allocate(zt(nz))
    allocate(time(nt))
    allocate(bounds(2,nt))

    p_in(:,:,:,:)    = 0.0
    t_in(:,:,:,:)    = 0.0
    qv_in(:,:,:,:)   = 0.0
    qc_in(:,:,:,:)   = 0.0
    qr_in(:,:,:,:)   = 0.0
    qi_in(:,:,:,:)   = 0.0
    qs_in(:,:,:,:)   = 0.0
    qg_in(:,:,:,:)   = 0.0
    !qh_in(:,:,:,:)   = 0.0     !CH2017: no hail
    w_in(:,:,:,:)    = 0.0
    qc_ad(:,:,:)     = 0.0
    wvp_out(:,:,:)   = 0.0
    lwp_out(:,:,:)   = 0.0
    lwp_ad_out(:,:,:)= 0.0
    iwp_out(:,:,:)   = 0.0
    all_out(:,:,:)   = 0.0
    hyd_out(:,:,:)   = 0.0
    cb_out(:,:,:)    = -999
    ct_out(:,:,:)    = -999
    wm_out(:,:,:)    = -999
    dqvsdz(:,:,:)    = -999
    mf_out(:,:,:)    = -999
    qv_cb(:,:,:)     = -999
    qvs_cb(:,:,:)    = -999
    p_cb(:,:,:)      = -999
    t_cb(:,:,:)      = -999

    cb_int(:,:)      = -999
    ct_int(:,:)      = -999

    t_inv(:)         = 0.0
    qvs_inv(:)       = 0.0

    rlat(:)          = 0.0
    rlon(:)          = 0.0
    time(:)          = 0.0

    ! Read in variables

    !print*,'READING VARIABLES'

    !write(*,*) 'time'
    status = nf90_inq_varid(ncid,"time", timeid)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    status = nf90_get_var(ncid,timeid,time)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    !write(*,*) 'time_bnds'
    status = nf90_inq_varid(ncid,"time_bnds", tbid)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    status = nf90_get_var(ncid,tbid,bounds)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    !write(*,*) 'rlon'
    status = nf90_inq_varid(ncid,"rlon", lonid)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    status = nf90_get_var(ncid,lonid,rlon)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    !write(*,*) 'rlat'
    status = nf90_inq_varid(ncid,"rlat", latid)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    status = nf90_get_var(ncid,latid,rlat)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    !write(*,*) 'P'
    status = nf90_inq_varid(ncid,"P", varid)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    status = nf90_get_var(ncid,varid,p_in)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    call fillWithNans(p_in)     ! CH2017 

    !write(*,*) 'T'
    status = nf90_inq_varid(ncid,"T", varid)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    status = nf90_get_var(ncid,varid,t_in)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    call fillWithNans(t_in)     ! CH2017  

    !write(*,*) 'QV'
    status = nf90_inq_varid(ncid,"QV", varid)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    status = nf90_get_var(ncid,varid,qv_in)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    call fillWithNans(qv_in)     ! CH2017  

    !write(*,*) 'QC'
    status = nf90_inq_varid(ncid,"QC", varid)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    status = nf90_get_var(ncid,varid,qc_in)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    call fillWithNans(qc_in)     ! CH2017  

    !write(*,*) 'QR'
    status = nf90_inq_varid(ncid,"QR", varid)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    status = nf90_get_var(ncid,varid,qr_in)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    call fillWithNans(qr_in)     ! CH2017  

    !write(*,*) 'QI'
    status = nf90_inq_varid(ncid,"QI", varid)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    status = nf90_get_var(ncid,varid,qi_in)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    call fillWithNans(qi_in)     ! CH2017  

    !write(*,*) 'QS'
    status = nf90_inq_varid(ncid,"QS", varid)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    status = nf90_get_var(ncid,varid,qs_in)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    call fillWithNans(qs_in)     ! CH2017  

    !write(*,*) 'QG'
    status = nf90_inq_varid(ncid,"QG", varid)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    status = nf90_get_var(ncid,varid,qg_in)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    call fillWithNans(qg_in)     ! CH2017  

    !CH2017: no hail
    !write(*,*) 'QH'
    !status = nf90_inq_varid(ncid,"QH", varid)
    !IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    !status = nf90_get_var(ncid,varid,qh_in)
    !IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    !write(*,*) 'W'
    status = nf90_inq_varid(ncid,"W", varid)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    status = nf90_get_var(ncid,varid,w_in)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    call fillWithNans(w_in)     ! CH2017  

    !CH2017: altitude levels are specific for given model output
    !        and set manually below.
    !write(*,*) 'vcoord'
    !status = nf90_inq_varid(ncid,"vcoord", varid)
    !IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)
    !status = nf90_get_var(ncid,varid,zm)
    !IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    ! MANUALLY SET ALTITUDE LEVELS THAT ARE IN DATASET. (CH2017)
    zt(1:61) = (/(i, i=0,6000,100)/)
    zt(62:65) = (/(i, i=7000,10000,1000)/)

    ! Calculations

    !do k=1,nz
    ! zt(k) = 0.5*(zm(k)+zm(k+1))
    !end do

    do t=1,nt

        ! calculate integrated quantities

        qt_in(:,:,:) = 0.
        ! CALCULATE water vapor path wvp
        call calcintpath(nx, ny, nz, qv_in(:,:,:,t), t_in(:,:,:,t), p_in(:,:,:,t), &
                    qv_in(:,:,:,t), qc_in(:,:,:,t), wvp_out(:,:,t), zt)

        ! CALCULATE liquid water path
        call calcintpath(nx, ny, nz, qc_in(:,:,:,t), t_in(:,:,:,t), p_in(:,:,:,t), &
                    qv_in(:,:,:,t), qc_in(:,:,:,t), lwp_out(:,:,t), zt, 1.e-6)

        ! UPDATE qt
        qt_in = qc_in(:,:,:,t) + qi_in(:,:,:,t)

        ! CALCULATE ice water path
        call calcintpath(nx, ny, nz, qi_in(:,:,:,t), t_in(:,:,:,t), p_in(:,:,:,t), &
                    qv_in(:,:,:,t), qt_in, iwp_out(:,:,t), zt, 1.e-6)

        ! UPDATE qt
        ! CH2017: no hail
        !qt_in = qc_in(:,:,:,t) + qr_in(:,:,:,t) + qi_in(:,:,:,t) + qs_in(:,:,:,t) + &
        !           qg_in(:,:,:,t) + qh_in(:,:,:,t)
        qt_in = qc_in(:,:,:,t) + qr_in(:,:,:,t) + qi_in(:,:,:,t) + qs_in(:,:,:,t) + &
                qg_in(:,:,:,t)

        ! CALCULATE hydrometeor path
        call calcintpath(nx, ny, nz, qt_in, t_in(:,:,:,t), p_in(:,:,:,t), &
                    qv_in(:,:,:,t), qt_in, hyd_out(:,:,t), zt)

        ! CALCULATE all water species path
        call calcintpath(nx, ny, nz, qv_in(:,:,:,t)+qt_in, t_in(:,:,:,t), p_in(:,:,:,t),&
                    qv_in(:,:,:,t), qt_in, all_out(:,:,t), zt, 1.e-6)

        ! determine cloud base and cloud top

        do j= 1, ny
        do i=1, nx
            if (lwp_out(i,j,t).ge.0.005) then ! CLOUD IN THIS VERTICAL COLUMN

                !cb = nz
                cb = 1

                !do while((qc_in(i,j,cb,t).lt.1.e-6).and.(cb.gt.1))
                ! CH2017: adjust to increasing vertical index with altitude instead of
                !         decreasing and check whether value is nan
                do while(isnan(qc_in(i,j,cb,t)).or.(qc_in(i,j,cb,t).lt.1.e-6).and.(cb.lt.nz))
                    !cb = cb -1
                    cb = cb + 1
                end do

                if (qi_in(i,j,cb,t)<1.e-10) then ! only cloud base if no ice present

                    ! SAVE CLOUD BASE HEIGHT AND INDEX
                    !cb_out(i,j,t) = 0.5*(zm(cb)+zm(cb+1))
                    cb_out(i,j,t) = zt(cb) ! CH2017: no vertical staggering
                    cb_int(i,j)   = cb ! save integer index
                    ct = cb

                    !do while(((qc_in(i,j,ct,t)+qi_in(i,j,ct,t)).gt.1.e-6).and.(ct.gt.1))
                    ! CH2017: adjust to increasing vertical index with altitude instead of
                    !         decreasing. no nan check necessary because ct > cb
                    !         and nan only present within topography.
                    do while(((qc_in(i,j,ct,t)+qi_in(i,j,ct,t)).gt.1.e-6).and.(ct.le.nz))
                        !ct = ct -1
                        ct = ct + 1
                    end do
                    !ct = ct+1 ! define cloud top to be the last level where cloud is found
                    ct = ct-1 ! CH2017: vertical index increasing with altitude 
                    !ct_out(i,j,t) = 0.5*(zm(ct)+zm(ct+1))
                    ct_out(i,j,t) = zt(ct) ! CH2017: no vertical staggering
                    ct_int(i,j)   = ct ! save integer index


                    ! determine top of warm part of cloud (liquid only, no ice)
                    ctw = cb
                    !do while((qc_in(i,j,ctw,t).gt.1.e-6).and.(ctw.gt.1))
                    ! CH2017: adjust to increasing vertical index with altitude instead of
                    !         decreasing.
                    do while((qc_in(i,j,ctw,t).gt.1.e-6).and.(ctw.lt.nz))
                        !ctw = ctw -1
                        ctw = ctw + 1 ! CH2017: vertical index increasing with altitude
                    end do
                    !ctw = ctw + 1
                    ctw = ctw - 1 ! CH2017 

                    mf = 0. ! integrated mass flux
                    wm = 0. ! integrated vertical velocity
                    zint = 0. ! integrated height
                    mint = 0. ! integrated mass

                    ! LOOP THROUGH CLOUD FROM BOTTOM TO TOP
                    !do k=cb,ct,-1
                    do k=cb,ct-1 ! CH2017
                        wmm = 0.5*(w_in(i,j,k,t)+w_in(i,j,k+1,t))
                        if (wmm.gt.0.) then
                            ! integrate w vertically and normalize by integrated height
                            !wm   = wm   + wmm*(zm(k)-zm(k+1))
                            !zint = zint + (zm(k)-zm(k+1))
                            ! CH2017: vertical index increasing with altitude
                            wm   = wm   + wmm*(zt(k+1)-zt(k))
                            zint = zint + (zt(k+1)-zt(k))
                        end if
                        if (wmm.gt.1.) then
                            ! determine mean convective mass flux, averaged between cloud
                            ! base and cloud top
                            ! integrate mass flux vertically and normalize by integrated mass
                            !tv = t_in(i,j,k,t)*(1.+ep2*qv_in(i,j,k,t) - qt_in(i,j,k))
                            ! CH2017: interpolate to centre between altitude levels
                            tv = 0.5*(t_in(i,j,k,t)*(1.+ep2*qv_in(i,j,k,t) - qt_in(i,j,k)) &
                                    + t_in(i,j,k+1,t)*(1.+ep2*qv_in(i,j,k+1,t) -&
                                                         qt_in(i,j,k+1)))
                            !dn = p_in(i,j,k,t)/(Rd*tv)
                            ! CH2017: interpolate to centre between altitude levels
                            dn = 0.5*(p_in(i,j,k,t) + p_in(i,j,k+1,t))/(Rd*tv)
                            !mf = mf + dn*wmm*(zm(k)-zm(k+1))
                            !mint = mint + dn*(zm(k)-zm(k+1))
                            ! CH2017: vertical index increases with altitude
                            mf = mf + dn*wmm*(zt(k+1)-zt(k))
                            mint = mint + dn*(zt(k+1)-zt(k))
                        end if
                    end do
                    if (zint>0) then
                        wm_out(i,j,t) = wm/zint
                    else
                        wm_out(i,j,t) = 0.
                    end if
                    if (mint>0) then
                        mf_out(i,j,t) = mf/mint
                    else
                        mf_out(i,j,t) = 0.
                    end if
                    qv_cb(i,j,t)  = qv_in(i,j,cb,t)
                    esatp         = fesatw(t_in(i,j,cb,t))
                    qvs_cb(i,j,t) = fqvs(esatp,p_in(i,j,cb,t))
                    p_cb(i,j,t)   = p_in(i,j,cb,t)
                    t_cb(i,j,t)   = t_in(i,j,cb,t)

                    ! determine adiabatic liquid water content (consider warm part only)

                    esatp         = fesatw(t_in(i,j,cb,t))
                    qvscb         = fqvs(esatp,p_in(i,j,cb,t))
                    !do k=cb,ctw,-1
                    do k=cb,ctw ! CH2017
                        esatp         = fesatw(t_in(i,j,k,t))
                        qvs           = fqvs(esatp,p_in(i,j,k,t))
                        qc_ad(i,j,k)  = qvscb - qvs
                    end do
                else ! ICE PRESENT AT CLOUD BASE. NO CLOUD 
                    cb_out(i,j,t) = mdv
                    ct_out(i,j,t) = mdv
                    mf_out(i,j,t) = mdv
                    wm_out(i,j,t) = mdv
                    qv_cb(i,j,t)  = mdv
                    qvs_cb(i,j,t) = mdv
                    p_cb(i,j,t)   = mdv
                    t_cb(i,j,t)   = mdv
                end if
            else ! NO CLOUD IN THIS VERTICAL COLUMN
                cb_out(i,j,t) = mdv
                ct_out(i,j,t) = mdv
                mf_out(i,j,t) = mdv
                wm_out(i,j,t) = mdv
                qv_cb(i,j,t)  = mdv
                qvs_cb(i,j,t) = mdv
                p_cb(i,j,t)   = mdv
                t_cb(i,j,t)   = mdv
            end if
        end do !i
        end do !j


        ! integrate adiabatic liquid water content vertically

        call calcintpath(nx, ny, nz, qc_ad, t_in(:,:,:,t), p_in(:,:,:,t), &
                    qv_in(:,:,:,t), qc_in(:,:,:,t), lwp_ad_out(:,:,t), zt, 1.e-6)
     

        ! Determine mean derivative of the saturation specific humidity qvs taken at constant
        ! saturation equivalent potential temperature theta_es. This corresponds to the
        ! environment that a condensed particle encounters in an updraft.

        do j= 1, ny
        do i=1, nx

            cb = cb_int(i,j)
            ct = ct_int(i,j)

            if ((lwp_out(i,j,t).ge.0.01).and.(wm_out(i,j,t).gt.0.)) then ! cloudy updraft
              ! use the formula of Bolton (1980) to compute theta_es
              ! in this case tstar = t

              theta_es = t_cb(i,j,t)*(p00/p_cb(i,j,t))**(0.2854*&
                        (1.-0.28*qvs_cb(i,j,t)))*exp(qvs_cb(i,j,t)*&
                        (1.+0.81*qvs_cb(i,j,t))*(3376./t_cb(i,j,t)-2.54))
              !call invert_thetaes(nz,cb,ct,theta_es,t_in(i,j,:,t),&
              !                  p_in(i,j,:,t),t_inv,qvs_inv,zm,zt)
              ! CH2017
              call invert_thetaes(nz,cb,ct,theta_es,t_in(i,j,:,t),&
                                p_in(i,j,:,t),t_inv,qvs_inv)

              ! calculate vertical gradient
              sum = 0.
              zint = 0. ! integrated height
              !do k=cb,ct,-1
              do k=cb,ct ! CH2017: adjust to vertical index increasing with altitude
                  !tmp    = (qvs_inv(k)-qvs_inv(k+1))/(zm(k)-zm(k+1))
                  tmp    = (qvs_inv(k)-qvs_inv(k-1))/(zt(k)-zt(k-1)) 
                  !sum    = sum + tmp* (zm(k)-zm(k+1))
                  !zint   = zint + (zm(k)-zm(k+1))
                  sum    = sum + tmp* (zt(k)-zt(k-1))
                  zint   = zint + (zt(k)-zt(k-1))
              end do
              if (zint>0) then
                  dqvsdz(i,j,t) = sum/zint
              else
                  dqvsdz(i,j,t) = -999
              end if
              if (dqvsdz(i,j,t) > 0.) dqvsdz(i,j,t) = -999
            end if ! cloudy updraft

        end do
        end do

    end do ! t


    !call  cscs_read_procstatm()
    deallocate(p_in)
    deallocate(t_in)
    deallocate(qv_in)
    deallocate(qc_in)
    deallocate(qr_in)
    deallocate(qi_in)
    deallocate(qs_in)
    deallocate(qg_in)
    !deallocate(qh_in) ! CH2017
    deallocate(w_in)
    deallocate(qt_in)

    ! write out results

    ! print*,'CREATE NEW NetCDF FILE'

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

    !* define variables

    iret = nf90_def_var(ncido, 'time', NF90_FLOAT,(/timedim/), timeid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'time_bnds', NF90_FLOAT,(/bndsdim,timedim/), tbid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'rlon', NF90_FLOAT,(/londim/), lonid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'rlat', NF90_FLOAT,(/latdim/), latid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'WVP', NF90_FLOAT,(/londim,latdim,timedim/),outvid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'LWP', NF90_FLOAT,(/londim,latdim,timedim/),outlid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'LWP_AD', NF90_FLOAT,(/londim,latdim,timedim/),outlaid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'IWP', NF90_FLOAT,(/londim,latdim,timedim/),outiid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'HYD', NF90_FLOAT,(/londim,latdim,timedim/),outhid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'ALL', NF90_FLOAT,(/londim,latdim,timedim/),outaid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'CB', NF90_FLOAT,(/londim,latdim,timedim/),outbid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'CT', NF90_FLOAT,(/londim,latdim,timedim/),outtid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'MF', NF90_FLOAT,(/londim,latdim,timedim/),outmfid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'WM', NF90_FLOAT,(/londim,latdim,timedim/),outwmid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'DQVSDZ', NF90_FLOAT,(/londim,latdim,timedim/),outdqid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'QV_CB', NF90_FLOAT,(/londim,latdim,timedim/),outqvcbid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'QVS_CB', NF90_FLOAT,(/londim,latdim,timedim/),outqvscbid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'P_CB', NF90_FLOAT,(/londim,latdim,timedim/),outpcbid)
    call check_err(iret)

    iret = nf90_def_var(ncido, 'T_CB', NF90_FLOAT,(/londim,latdim,timedim/),outtcbid)
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

    iret = nf90_put_att(ncido, outlid,'standard_name','liquid water path')
    call check_err(iret)
    iret = nf90_put_att(ncido, outlid,'long_name','liquid water path')
    call check_err(iret)
    iret = nf90_put_att(ncido, outlid,'units','kg m-2')
    call check_err(iret)

    iret = nf90_put_att(ncido, outlaid,'standard_name','adiabatic liquid water path')
    call check_err(iret)
    iret = nf90_put_att(ncido, outlaid,'long_name','adiabatic liquid water path')
    call check_err(iret)
    iret = nf90_put_att(ncido, outlaid,'units','kg m-2')
    call check_err(iret)

    iret = nf90_put_att(ncido, outiid,'standard_name','ice path')
    call check_err(iret)
    iret = nf90_put_att(ncido, outiid,'long_name','ice path')
    call check_err(iret)
    iret = nf90_put_att(ncido, outiid,'units','kg m-2')
    call check_err(iret)

    iret = nf90_put_att(ncido, outhid,'standard_name','all hydrometeors path')
    call check_err(iret)
    iret = nf90_put_att(ncido, outhid,'long_name','hydrometeor')
    call check_err(iret)
    iret = nf90_put_att(ncido, outhid,'units','kg m-2')
    call check_err(iret)

    iret = nf90_put_att(ncido, outaid,'standard_name','all water path')
    call check_err(iret)
    iret = nf90_put_att(ncido, outaid,'long_name','all water path')
    call check_err(iret)
    iret = nf90_put_att(ncido, outaid,'units','kg m-2')
    call check_err(iret)

    iret = nf90_put_att(ncido, outbid,'standard_name','cloud base height')
    call check_err(iret)
    iret = nf90_put_att(ncido, outbid,'long_name','cloud base height')
    call check_err(iret)
    iret = nf90_put_att(ncido, outbid,'units','m')
    call check_err(iret)
    iret = nf90_put_att(ncido, outbid,'_FillValue',-999.)
    call check_err(iret)

    iret = nf90_put_att(ncido, outtid,'standard_name','cloud top height')
    call check_err(iret)
    iret = nf90_put_att(ncido, outtid,'long_name','cloud top height')
    call check_err(iret)
    iret = nf90_put_att(ncido, outtid,'units','m')
    call check_err(iret)
    iret = nf90_put_att(ncido, outtid,'_FillValue',-999.)
    call check_err(iret)

    iret = nf90_put_att(ncido, outmfid,'standard_name','mean upward velocity')
    call check_err(iret)
    iret = nf90_put_att(ncido, outmfid,'long_name','mean upward velocity, density weighted')
    call check_err(iret)
    iret = nf90_put_att(ncido, outmfid,'units','m s-1')
    call check_err(iret)
    iret = nf90_put_att(ncido, outmfid,'_FillValue',-999.)
    call check_err(iret)

    iret = nf90_put_att(ncido, outwmid,'standard_name','mean upward velocity')
    call check_err(iret)
    iret = nf90_put_att(ncido, outwmid,'long_name','mean upward velocity')
    call check_err(iret)
    iret = nf90_put_att(ncido, outwmid,'units','m s-1')
    call check_err(iret)
    iret = nf90_put_att(ncido, outwmid,'_FillValue',-999.)
    call check_err(iret)

    iret = nf90_put_att(ncido, outdqid,'standard_name','vertical gradient of qvs')
    call check_err(iret)
    iret = nf90_put_att(ncido, outdqid,'long_name','vertical gradient of qvs along moist adiabat')
    call check_err(iret)
    iret = nf90_put_att(ncido, outdqid,'units','kg kg-1 s-1')
    call check_err(iret)
    iret = nf90_put_att(ncido, outdqid,'_FillValue',-999.)
    call check_err(iret)

    iret = nf90_put_att(ncido, outqvcbid,'standard_name','specific humidity at cloud base')
    call check_err(iret)
    iret = nf90_put_att(ncido, outqvcbid,'long_name','specific humidity at cloud-base height')
    call check_err(iret)
    iret = nf90_put_att(ncido, outqvcbid,'units','kg kg-1')
    call check_err(iret)
    iret = nf90_put_att(ncido, outqvcbid,'_FillValue',-999.)
    call check_err(iret)

    iret = nf90_put_att(ncido, outqvscbid,'standard_name','saturation specific humidity at cloud base')
    call check_err(iret)
    iret = nf90_put_att(ncido, outqvscbid,'long_name','saturation specific humidity at cloud-base height')
    call check_err(iret)
    iret = nf90_put_att(ncido, outqvscbid,'units','kg kg-1')
    call check_err(iret)
    iret = nf90_put_att(ncido, outqvscbid,'_FillValue',-999.)
    call check_err(iret)
    iret = nf90_put_att(ncido, outpcbid,'_FillValue',-999.)
    call check_err(iret)
    iret = nf90_put_att(ncido, outtcbid,'_FillValue',-999.)
    call check_err(iret)

    iret = nf90_put_att(ncido, outpcbid,'standard_name','pressure at cloud base')
    call check_err(iret)
    iret = nf90_put_att(ncido, outpcbid,'long_name','pressure at cloud-base height')
    call check_err(iret)
    iret = nf90_put_att(ncido, outpcbid,'units','Pa')
    call check_err(iret)
    iret = nf90_put_att(ncido, outpcbid,'_FillValue',-999.)
    call check_err(iret)

    iret = nf90_put_att(ncido, outtcbid,'standard_name','temperature at cloud base')
    call check_err(iret)
    iret = nf90_put_att(ncido, outtcbid,'long_name','temperature at cloud-base height')
    call check_err(iret)
    iret = nf90_put_att(ncido, outtcbid,'units','K')
    call check_err(iret)
    iret = nf90_put_att(ncido, outtcbid,'_FillValue',-999.)
    call check_err(iret)

    status = nf90_inq_varid(ncid,"T", varid)
    iret = nf90_get_att(ncid, varid,'grid_mapping',name)
    call check_err(iret)
    iret = nf90_put_att(ncido, outvid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outlid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outlaid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outiid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outhid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outaid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outbid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outtid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outmfid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outwmid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outdqid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outqvcbid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outqvscbid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outpcbid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outtcbid,'grid_mapping',trim(name))
    call check_err(iret)
    iret = nf90_get_att(ncid, varid,'coordinates',name)
    call check_err(iret)
    iret = nf90_put_att(ncido, outvid,'coordinates',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outlid,'coordinates',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outlaid,'coordinates',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outiid,'coordinates',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outhid,'coordinates',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outaid,'coordinates',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outbid,'coordinates',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outtid,'coordinates',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outmfid,'coordinates',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outwmid,'coordinates',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outdqid,'coordinates',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outqvcbid,'coordinates',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outqvscbid,'coordinates',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outtcbid,'coordinates',trim(name))
    call check_err(iret)
    iret = nf90_put_att(ncido, outpcbid,'coordinates',trim(name))
    call check_err(iret)

    !* leave define mode
    STATUS = NF90_ENDDEF(ncido)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    !* store variables
    STATUS = NF90_PUT_VAR(ncido, timeid,time)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, tbid,bounds)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, lonid, rlon)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, latid, rlat)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outvid,wvp_out)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outlid,lwp_out)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outlaid,lwp_ad_out)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outiid,iwp_out)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outhid,hyd_out)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outaid,all_out)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outbid,cb_out)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outtid,ct_out)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outmfid,mf_out)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outwmid,wm_out)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outdqid,dqvsdz)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outqvcbid,qv_cb)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outqvscbid,qvs_cb)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outtcbid,t_cb)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_PUT_VAR(ncido, outpcbid,p_cb)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_CLOSE(ncido)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    STATUS = NF90_CLOSE(NCID)
    IF (STATUS .NE. NF90_NOERR) PRINT *, NF90_STRERROR(STATUS)

    deallocate(wvp_out)
    deallocate(lwp_out)
    deallocate(iwp_out)
    deallocate(hyd_out)
    deallocate(all_out)
    deallocate(cb_out)
    deallocate(ct_out)
    deallocate(mf_out)
    deallocate(wm_out)
    deallocate(qv_cb)
    deallocate(qvs_cb)
    deallocate(p_cb)
    deallocate(t_cb)

    deallocate(rlon)
    deallocate(rlat)
    !deallocate(zm) ! CH2017
    deallocate(time)
    deallocate(bounds)

    CALL SYSTEM_CLOCK(COUNT=icountnew)

    rt = ( REAL(icountnew) - REAL(icountold) ) / REAL(icountrate)
    ! write(*,"(A,F8.2,A)") "time : ", rt*1e3, ' ms' 

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


    subroutine calcintpath(nx, ny, nz, varin, t, p, &
                            q, qt, varout, zt, threshold)

    implicit none

    real, intent(in), dimension(:,:,:) :: varin, t, q, p, qt
    real, intent(in), dimension(:) :: zt ! CH2017: Altitude of input values
    integer, intent(in) :: nx, ny, nz
    real, intent(out), dimension(:,:)  :: varout
    real, intent(in), optional :: threshold

    integer :: i, j, k
    real :: thres
    real :: dn, dnk, dnkm1, tvk, tvkm1, varmean
    real :: nan ! CH2017: used to test for nan

    real, parameter :: Rd  = 287.04
    real, parameter :: Rm  = 461.5
    real, parameter :: ep2 = Rm/Rd - 1.

    ! CH2017: create nan
    nan = 3.
    call createNan(nan)

    varout = 0.

    if (present(threshold)) then
       thres = threshold
    else
       thres = 0.0
    end if

    ! CH2017: Because vertical variables are given at altitude levels
    !         there is no vertical staggering.
    !         Integration is performed over the distance between two levels
    !         with the quantities interpolated to the midpoint between the two levels.
    !do k=nz, 1, -1     
    do k=2, nz   ! CH2017: vertical index increases with altitude
        do j=1, ny
            do i=1, nx
                !tv = t(i,j,k)*(1. + ep2*q(i,j,k) - qt(i,j,k)) ! qt is the loading
                ! CH2017: take values at this altitude and altitude below
                ! tv at level of k
                tvk = t(i,j,k)*(1. + ep2*q(i,j,k) - qt(i,j,k)) 
                ! tv at level of k-1
                tvkm1 = t(i,j,k-1)*(1. + ep2*q(i,j,k-1) - qt(i,j,k-1)) 
                ! CH2017: take values at this altitude and altitude below
                dnk = p(i,j,k)/(Rd*tvk) ! [kg/m^3] dn at level of k
                dnkm1 = p(i,j,k-1)/(Rd*tvkm1) ! [kg/m^3] dn at level of k-1
                ! CH2017: calculate mean values between the two altitdue levels
                dn = 0.5*(dnk+dnkm1) ! mean dn ('density') between level k and k-1
                varmean = 0.5*(varin(i,j,k)+varin(i,j,k-1))
                !if (varin(i,j,k) > thres) then 
                if ((varmean > thres).and.(varmean.ne.nan)) then ! CH2017: nan check
                   !varout(i,j) = varout(i,j)+varin(i,j,k)*(zm(k)-zm(k+1))*dn 
                   varout(i,j) = varout(i,j)+varmean*(zt(k)-zt(k-1))*dn ! CH2017
                end if
                if (varout(i,j) > 1e10) varout(i,j) = 0.
            enddo
        end do
    end do
    end subroutine calcintpath

    subroutine invert_thetaes(nz,cb,ct,theta_es,t_in,p_in,t_inv,qvs_inv)

    implicit none

    real, intent(in), dimension(:)  :: t_in, p_in
    integer, intent(in)             :: nz, cb, ct
    real, intent(out), dimension(:) :: t_inv, qvs_inv
    real, intent(in)                :: theta_es

    integer :: k, iter
    real :: dn, tv, the, qvs, tguess, tg_old

    real, parameter :: Rd  = 287.04
    real, parameter :: Rm  = 461.5
    real, parameter :: ep2 = Rm/Rd - 1.
    real, parameter :: eps = 1.e-5

    !do k=cb+1,ct,-1
    do k=cb-1,ct ! CH2017: vertical levels increase with height 

       iter   = 0
       tguess = t_in(k)
       esatp  = fesatw(tguess)
       qvs    = fqvs(esatp,p_in(k))

       the    = tguess*(p00/p_in(k))**(0.2854*(1.-0.28*qvs))*&
                        exp(qvs*(1.+0.81*qvs)*(3376./tguess-2.54))

       tg_old = tguess
       do while (the-theta_es.gt.eps)
          tg_old = tguess
          tguess = tguess-0.01
          iter   = iter+1
          esatp  = fesatw(tguess)
          qvs    = fqvs(esatp,p_in(k))
          the    = tguess*(p00/p_in(k))**(0.2854*(1.-0.28*qvs))*&
                        exp(qvs*(1.+0.81*qvs)*(3376./tguess-2.54))
       end do
       !write(*,*) iter

       t_inv(k)   = 0.5*(tguess+tg_old)
       esatp      = fesatw(t_inv(k))
       qvs        = fqvs(esatp,p_in(k))
       qvs_inv(k) = qvs

    end do

    end subroutine invert_thetaes

    !! --- CSCS (Swiss National Supercomputing Center) ---
    subroutine cscs_read_procstatm()

    implicit none
    character(len=20) :: file
    integer :: size=0, resident=0, share=0, text=0, lib=0, data=0, dt=0
    integer:: ierr=0

    file='/proc/self/statm'
    open(unit=1,file=file,form='formatted',STATUS='OLD',ACTION='READ',IOSTAT=ierr)
    read(unit=1,FMT=*,IOSTAT=ierr) size, resident, share, text, lib, data, dt
    close(unit=1)

    if (ierr < 0) then
    write(*,*)'Problem reading /proc/self/statm'
    else
    write(*,'(a,i8)') '/proc/self/statm size = ', size
    write(*,'(a,i8)') '/proc/self/statm resi = ', resident
    write(*,'(a,i8)') '/proc/self/statm data = ', data
    end if
    end subroutine cscs_read_procstatm

    ! CH2017
    ! USED TO PRODUCE A NAN VALUES FROM ANY INPUT VALUE
    subroutine createNan(a)
        real, intent(inout) :: a
        a = (a-a)/(a-a) 
    end subroutine

    ! CH2017
    ! FILLS THE INPUT ARRAYS WITH NAN, WHERE THE ARRAYS HAVE VALUE nanIn
    subroutine fillWithNans(array)
        real, intent(out), dimension(:,:,:,:)  :: array
        real :: nan = 3.
        real, parameter :: nanIn = 9.96920997E+36

        call createNan(nan)
        
        do k = 1,nz
        do i = 1,nx
        do j = 1,ny
            if (array(i,j,k,1).eq.nanIn) then
                array(i,j,k,1) = nan
            end if
        end do
        end do
        end do
    end subroutine
end Program lwp