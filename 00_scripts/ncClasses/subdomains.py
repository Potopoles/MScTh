def setSSI(i_subdomain, ssI):
    # These indices are used for 4.4 km
    if i_subdomain == 0:
        domainName = 'Whole_Domain'
        lon0 = 0
        lon1 = 261 
        lat0 = 0
        lat1 = 245
    elif i_subdomain == 1:
        domainName = 'Alpine_Region'
        lon0 = 50
        lon1 = 237
        lat0 = 41
        lat1 = 155
    elif i_subdomain == 2:
        domainName = 'Northern_Italy'
        lon0 = 102 
        lon1 = 150 
        lat0 = 65 
        lat1 = 97 
    elif i_subdomain == 22:
        domainName = 'Northern_Italy2'
        lon0 = 100 
        lon1 = 150 
        lat0 = 71
        lat1 = 94
    elif i_subdomain == 3:
        domainName = 'South_Western_Alps'
        lon0 = 50 
        lon1 = 115 
        lat0 = 35 
        lat1 = 90 
    elif i_subdomain == 4:
        domainName = 'Close_Up_Crossect'
        #lon0 = 110 
        #lon1 = 110
        lon0 = 110 
        lon1 = 140
        #lat0 = 75  
        lat0 = 40
        lat1 = 135 
    elif i_subdomain == 5:
        domainName = 'Mountain'
        lon0 = 95
        lon1 = 188
        lat0 = 95
        lat1 = 135
    elif i_subdomain == 6:
        domainName = 'Plain'
        lon0 = 115
        lon1 = 210
        lat0 = 55
        lat1 = 95
    elif i_subdomain == 9:
        domainName = 'Test_Domain'
        lon0 = 130 
        lon1 = 131 
        lat0 = 120  
        lat1 = 121 
    elif i_subdomain == 10:
        domainName = 'Summary_Crossect'
        lon0 = 110
        lon1 = 135
        lat0 = 52
        lat1 = 135 
    elif i_subdomain == 11:
        domainName = 'Alpine_Ridge'
        lon0 = 110 
        lon1 = 150 
        lat0 = 110 
        lat1 = 120 
    elif i_subdomain == 12:
        domainName = 'Alpine_Ridge_Vert_Prof'
        lon0 = 100 
        lon1 = 160
        lat0 = 100
        lat1 = 125

    ssI['lon0'] = lon0
    ssI['lon1'] = lon1
    ssI['lat0'] = lat0
    ssI['lat1'] = lat1
         
    ssI['rlon'] = [lon0,lon1]
    ssI['rlat'] = [lat0,lat1]
    ssI['x_1'] = [lon0,lon1]
    ssI['y_1'] = [lat0,lat1]


    # FOR THE cloud-base etc. frequency dists
    ssI['4']['rlon'] = list(range(lon0,lon1))
    ssI['4']['rlat'] = list(range(lat0,lat1)) 
    ssI['4']['srlon'] = list(range(lon0,lon1)) 
    ssI['4']['srlat'] = list(range(lat0,lat1)) 
    ssI['2']['rlon'] = list(range(lon0*2,lon1*2))
    ssI['2']['rlat'] = list(range(lat0*2,lat1*2)) 
    ssI['2']['srlon'] = list(range(lon0*2,lon1*2)) 
    ssI['2']['srlat'] = list(range(lat0*2,lat1*2)) 
    ssI['1']['rlon'] = list(range(lon0*4,lon1*4))
    ssI['1']['rlat'] = list(range(lat0*4,lat1*4)) 
    ssI['1']['srlon'] = list(range(lon0*4,lon1*4)) 
    ssI['1']['srlat'] = list(range(lat0*4,lat1*4)) 

    return(ssI, domainName)
