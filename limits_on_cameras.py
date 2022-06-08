import pandas as pd

def define_limits():
    ## limits camera 1...
    x11,y11 = 1.426354847298914,43.55539786693758
    x12,y12 = 1.426261158591022,43.55479984902253
    x13,y13 = 1.426409472457491,43.55478414633177
    x14,y14 = 1.426504152219241,43.55539384049879
    ## limits camera 2...
    x21,y21 = 1.426527894356817,43.55539825174612
    x22,y22 = 1.426459574895029,43.55492290207174
    x23,y23 = 1.42799408459108,43.55480046538784
    x24,y24 = 1.428158178407755,43.55525239586236
    ## limits camera 3...
    x31,y31 = 1.429652281838212,43.55514285890079
    x32,y32 = 1.429592567016844,43.55470070819603
    x33,y33 = 1.43024434693656,43.55465100238456
    x34,y34 = 1.430451747987254,43.55505111989425
    ## limits camera 4...
    x41,y41 = 1.431263456832792,43.55516290867535
    x42,y42 = 1.431197537266506,43.55450412110343
    x43,y43 = 1.431986442572628,43.55442356678335
    x44,y44 = 1.43212521207108,43.55507673638063
    ## limits camera 5...
    x51,y51 = 1.430029842941234,43.55513456631824
    x52,y52 = 1.429971091517508,43.5545989853197
    x53,y53 = 1.431176762629895,43.55450848370832
    x54,y54 = 1.431249694278955,43.55515640727656
    ## limits camera 6...
    x61,y61 = 1.428159577002355,43.55530735951356
    x62,y62 = 1.427996372008276,43.55475527266172
    x63,y63 = 1.429962871340589,43.55458700568892
    x64,y64 = 1.43001107849146,43.55512619188122

    # create dataframe
    df_columns = ["Camera_number", "Inside FOV", 'x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'x4', 'y4']
    df = pd.DataFrame(columns=df_columns)

    ## Insert camera 1
    df.loc[0,'Camera_number'] = 1
    df.loc[0,'x1'] = x11
    df.loc[0,'x2'] = x12
    df.loc[0,'x3'] = x13
    df.loc[0,'x4'] = x14
    df.loc[0,'y1'] = y11
    df.loc[0,'y2'] = y12
    df.loc[0,'y3'] = y13
    df.loc[0,'y4'] = y14
    ## Insert camera 2
    df.loc[1,'Camera_number'] = 2
    df.loc[1,'x1'] = x21
    df.loc[1,'x2'] = x22
    df.loc[1,'x3'] = x23
    df.loc[1,'x4'] = x24
    df.loc[1,'y1'] = y21
    df.loc[1,'y2'] = y22
    df.loc[1,'y3'] = y23
    df.loc[1,'y4'] = y24
    ## Insert camera 3
    df.loc[2,'Camera_number'] = 3
    df.loc[2,'x1'] = x31
    df.loc[2,'x2'] = x32
    df.loc[2,'x3'] = x33
    df.loc[2,'x4'] = x34
    df.loc[2,'y1'] = y31
    df.loc[2,'y2'] = y32
    df.loc[2,'y3'] = y33
    df.loc[2,'y4'] = y34
    ## Insert camera 4
    df.loc[3,'Camera_number'] = 4
    df.loc[3,'x1'] = x41
    df.loc[3,'x2'] = x42
    df.loc[3,'x3'] = x43
    df.loc[3,'x4'] = x44
    df.loc[3,'y1'] = y41
    df.loc[3,'y2'] = y42
    df.loc[3,'y3'] = y43
    df.loc[3,'y4'] = y44
    ## Insert camera 5
    df.loc[4,'Camera_number'] = 5
    df.loc[4,'x1'] = x51
    df.loc[4,'x2'] = x52
    df.loc[4,'x3'] = x53
    df.loc[4,'x4'] = x54
    df.loc[4,'y1'] = y51
    df.loc[4,'y2'] = y52
    df.loc[4,'y3'] = y53
    df.loc[4,'y4'] = y54
    ## Insert camera 6
    df.loc[5,'Camera_number'] = 6
    df.loc[5,'x1'] = x61
    df.loc[5,'x2'] = x62
    df.loc[5,'x3'] = x63
    df.loc[5,'x4'] = x64
    df.loc[5,'y1'] = y61
    df.loc[5,'y2'] = y62
    df.loc[5,'y3'] = y63
    df.loc[5,'y4'] = y64

    # return dataframe with gps limits for all cameras
    return(df)