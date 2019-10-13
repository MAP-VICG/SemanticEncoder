# '''
# Created on Jul 29, 2019
# 
# @author: damaresresende
# '''
import numpy as np
import matplotlib.pyplot as plt
 
 
cats = ['ALL', 'COLOR', 'TEXTURE', 'PARTS', 'SHAPE', '_COLOR', '_TEXTURE', '_PARTS', '_SHAPE']
loss = {key: np.zeros((50,10)) for key in cats}
acc = {key: np.zeros((50,10)) for key in cats}
 
res_loss = {key: [] for key in cats}
res_acc = {key: [] for key in cats}
 
for i in range(10):
    for flag in cats:
        with open('/Users/damaresresende/Desktop/nfold' + str(i) + '/' + flag + '/history.txt') as f:
            for row in f.readlines():
                if row.startswith('loss'):
                    for k, v in enumerate((row.split('loss:')[1]).split(',')):
                        loss[flag][k,i] = float(v)
#                     loss[flag].append([float(v) for v in (row.split('loss:')[1]).split(',')])
                if row.startswith('acc'):
                    for k, v in enumerate((row.split('acc:')[1]).split(',')):
                        acc[flag][k,i] = float(v)
#                     acc[flag].append([float(v) for v in (row.split('acc:')[1]).split(',')])
 
for flag in cats:
    res_loss[flag].append(np.average(loss[flag], 1))
    res_loss[flag].append(np.std(loss[flag], 1))
     
    res_acc[flag].append(np.average(acc[flag], 1))
    res_acc[flag].append(np.std(acc[flag], 1))
     
upperlimits = [True, False] * 25
lowerlimits = [False, True] * 25
 
lbs = ['Cor', 'Textura', 'Partes', 'Forma']
 
clrs = ['#00CC00', '#CC0000', '#0000CC', '#FF8000']
 
for i, flag in enumerate(['COLOR', 'TEXTURE', 'PARTS', 'SHAPE']):
    plt.errorbar([x for x in range(50)], res_acc[flag][0], res_acc[flag][1], uplims=upperlimits, lolims=lowerlimits, label=lbs[i], color=clrs[i])
 
plt.legend(loc='top right')
plt.xlabel('Épocas', fontsize=14)
# plt.ylabel('Loss (MSE)', fontsize=14)
plt.ylabel('Acurácia', fontsize=14)
plt.show()
 
lbs = ['Sem Cor', 'Sem Textura', 'Sem Partes', 'Sem Forma']
 
for i, flag in enumerate(['_COLOR', '_TEXTURE', '_PARTS', '_SHAPE']):
    plt.errorbar([x for x in range(50)], res_acc[flag][0], res_acc[flag][1], uplims=upperlimits, lolims=lowerlimits, label=lbs[i], color=clrs[i])
 
plt.legend(loc='top right')
plt.xlabel('Épocas', fontsize=14)
# plt.ylabel('Loss (MSE)', fontsize=14)
plt.ylabel('Acurácia', fontsize=14)
plt.show()
 
lbs = ['Cor', 'Textura', 'Partes', 'Forma']
 
for i, flag in enumerate(['COLOR', 'TEXTURE', 'PARTS', 'SHAPE']):
    plt.errorbar([x for x in range(50)], res_loss[flag][0], res_loss[flag][1], uplims=upperlimits, lolims=lowerlimits, label=lbs[i], color=clrs[i])
 
plt.legend(loc='top right')
plt.xlabel('Épocas', fontsize=14)
plt.ylabel('Loss (MSE)', fontsize=14)
# plt.ylabel('Acurácia (F1-Score)', fontsize=14)
plt.show()
 
lbs = ['Sem Cor', 'Sem Textura', 'Sem Partes', 'Sem Forma']
 
for i, flag in enumerate(['_COLOR', '_TEXTURE', '_PARTS', '_SHAPE']):
    plt.errorbar([x for x in range(50)], res_loss[flag][0], res_loss[flag][1], uplims=upperlimits, lolims=lowerlimits, label=lbs[i], color=clrs[i])
 
plt.legend(loc='top right')
plt.xlabel('Épocas', fontsize=14)
plt.ylabel('Loss (MSE)', fontsize=14)
# plt.ylabel('Acurácia (F1-Score)', fontsize=14)
plt.show()
              
print('done')

# from matplotlib import pyplot as plt
# loss = {
#     'NCR': [0.9329599486326657,0.5173726486366165,0.4603724764846772,0.42844945866367373,0.4075388900862345,0.3868032149260878,0.3673659835122284,0.35224612419366186,0.3367227978765752,0.3248615503373544,0.3117781166304648,0.3002189406159285,0.29148509373394343,0.28322935799112975,0.27640490684145935,0.2713952169798647,0.26610644962439756,0.26100985897817647,0.2559821759204573,0.25203853760749845,0.24850924670920851,0.24637156789999565,0.24176374451183788,0.23860458971030646,0.23550675641998778,0.23417305875603114,0.22980615912445523,0.22689515302838553,0.2248965730546333,0.22396984893968222,0.22283180265751548,0.2203098424083148,0.21782046096055907,0.21610323504558637,0.21299304768882937,0.21155919420599364,0.21079545935090677,0.20840991598518668,0.20735531757323095,0.2064100036442417,0.20364430425417632,0.20345964779570833,0.2029388072296294,0.2007842330228142,0.19829825796990158,0.19782128165662602,0.19629017113953023,0.19468632648935472,0.19489924044309112,0.19322433993173538],
#     'NPT': [0.8032259548885792,0.49805953687071325,0.43686609726983283,0.4018159895929453,0.37759435227133376,0.3553657325461541,0.3337861540229195,0.31944701782025525,0.3050736338455407,0.2937717811917071,0.28528285665019976,0.27586360490169887,0.26903783261139624,0.2630877356112989,0.2566397694106977,0.2523025873517401,0.24749556111695503,0.2423700541289052,0.2386682538038421,0.2353819171317282,0.23121536856781172,0.2296661459584852,0.22520876233675552,0.22394438795721977,0.22085775472340735,0.2200128617004942,0.21858619553650527,0.21603232593011826,0.21422332354936485,0.21216308260552924,0.20995318521409198,0.208474595915555,0.2060998937556852,0.20522359145256622,0.20422612804173176,0.2018222695436841,0.19997654254276284,0.19867525247941586,0.1976643476827838,0.19663522302455574,0.1959657138302807,0.19339770219716312,0.1926387790065693,0.19133630546411512,0.1914176581561977,0.19094588313425637,0.1897551338131617,0.1901023780486063,0.18855527566333732,0.18732515427640525],
#     'NSP': [0.6069684562185007,0.36791773314927195,0.3150466939295988,0.28513591460460946,0.2622236672993956,0.2454378136505211,0.2316030229556653,0.22053847629666604,0.211466258739936,0.203373576218747,0.19610725245217236,0.18985808316523844,0.18428236074544457,0.18175084647247425,0.17774271400984995,0.1744542168034952,0.16890757837404335,0.16723136860430426,0.1651305787210712,0.1628898540232155,0.16055882287145234,0.15801888277634482,0.15546713747413232,0.15361207117526782,0.15237634168438316,0.15000298086921116,0.1488190151874256,0.14722977413501304,0.14550502460722098,0.1448256096119708,0.14371733648122692,0.14196514145509953,0.14038913513991733,0.13924020174372165,0.1391166788702708,0.13700504434677704,0.13686908337519413,0.13532365318220083,0.1346717243055332,0.1340885743795141,0.13263001799683255,0.13196046758588947,0.13096584872531172,0.1303311135545794,0.12954254752051914,0.12984236584114983,0.12812652176510023,0.12740573566629218,0.12710446489014485,0.12696254409791935],
#     'NTX': [0.8907495919919948,0.5156981451792874,0.4663641081997758,0.43808152433317127,0.4136475316932168,0.39325249845796434,0.3754369668639153,0.35917066080889143,0.3452236158605248,0.33302263448446495,0.3203088522681088,0.3091314948301373,0.3012338942567599,0.2926653171923212,0.28487316149035236,0.2823305385629827,0.2770312672557755,0.2709067691562813,0.2674517800462578,0.26344463338793533,0.2585325663661717,0.25263851338508914,0.2483321335011505,0.24702862634278502,0.24339454436317157,0.2404180908517556,0.23930683892679583,0.2361119395136359,0.23233066747284395,0.22951756359793687,0.22890749900428875,0.2268622804410492,0.22426738931477905,0.22235414323720418,0.22115743518474587,0.2197338178158056,0.21659430552033018,0.21569898195076567,0.21484732311753166,0.2136201203218783,0.21268874222460665,0.21128515288973043,0.21038327666663564,0.21133416971327845,0.20911928508005706,0.20715058448363577,0.20612575727912055,0.20522573367930966,0.2042301818369721,0.20367384007130804],
#     'ALL': [0.9479712882974244,0.5236619201843424,0.4663975290818421,0.43746592656248956,0.41548170103347026,0.40019095512721137,0.3841111157912202,0.36913013270466755,0.35713693091054327,0.34355172599512385,0.3315151205678253,0.32284544765487583,0.3159067838891221,0.3087601186454558,0.3000314559738382,0.29502720708799135,0.29056395258593065,0.2845377421139523,0.27999030056672536,0.2755749613140227,0.27284202088065945,0.2689151877497988,0.26606884847407014,0.26123015520112,0.2606624954810371,0.25876311680088737,0.25602590972119005,0.25300475384416954,0.25081671405367606,0.24945639867724698,0.24716227516759656,0.2457544279517752,0.24452945108141189,0.2425653813828328,0.24160336467145202,0.24031673931154668,0.2383223847799379,0.2361744586595911,0.23488237950213914,0.2336409306448824,0.24022139907881435,0.23434329695012346,0.23082773595555497,0.23032319490658032,0.22696321843332742,0.2264006176346986,0.22427831765358633,0.2226674186283758,0.22272004658628863,0.22125836101840024],
#     'CR': [0.4014132799365068,0.257609932810561,0.21663214301236983,0.18961984264768267,0.17175552802765148,0.15922410080553673,0.15054986094839531,0.14307109568254803,0.13545670447637528,0.13095786052753866,0.12725735446486933,0.12281484505123041,0.1208685876791862,0.1183143176414464,0.11428934538497919,0.11104060404341116,0.10896241776746562,0.10672515577162713,0.10533555182754083,0.10489469050568767,0.10234015919073172,0.10026037605993664,0.09895799875677393,0.09834529358378159,0.09654448938926244,0.09584935928067329,0.09384325057211994,0.09257378157728108,0.09214133001881113,0.09102285671819323,0.08973878365550451,0.08981742931162186,0.0884085971923685,0.08751594537137217,0.08690109175101768,0.0860336734518886,0.08551913008783212,0.08551796248187724,0.08397434825693335,0.08336721188869341,0.0829975944764948,0.08291295592146537,0.08345413427641633,0.08210622681773105,0.08142729472959294,0.08008846592112069,0.08013099110729155,0.079253760245035,0.0793128288822217,0.0781699308069251],
#     'PT': [0.545326986505268,0.32273837443872405,0.2707470419293596,0.24177288386221332,0.22156387754182374,0.20479368920265842,0.1923215325959986,0.18301781301583758,0.17505097907158979,0.16903169324439465,0.1614030859629829,0.1567135617327236,0.15262962779116376,0.15022332837934996,0.14591515783625267,0.14157209253246275,0.1386118986715401,0.1357479452743724,0.1335416625952007,0.13286498440454914,0.1302315157478465,0.12799155124846626,0.12534529389179924,0.12557279947589126,0.12281434693913193,0.1215739061268698,0.11977453404998141,0.11879354680691251,0.1173002714417159,0.1166769395422706,0.11451219568036454,0.11440242156370779,0.1123098120377207,0.1113033398820537,0.11073143525941616,0.1096548162707979,0.10875947284903116,0.10878127344281747,0.10719510167712369,0.10648564096834212,0.10555550212175846,0.10604669556929423,0.10445855935734887,0.10358576589338646,0.10260084096029609,0.10226705152169416,0.1014311254448738,0.10052212225154326,0.10025489973034947,0.09942769987583909],
#     'SP': [0.7456579686558743,0.46535935928588484,0.4092944468854485,0.3718349599553772,0.34478683521215053,0.3244764239812511,0.30787177135786153,0.29342679525110443,0.2792018425784052,0.2680502198581943,0.25972589467119317,0.2539053627442485,0.2501290491854069,0.24317165434123433,0.2396768692686689,0.23523690561594912,0.23277463089329242,0.2287697680012212,0.2259825396081107,0.22157836073620787,0.22113230649100354,0.2180607595458948,0.21686509103175608,0.21494865584178827,0.21214059975285995,0.21066590661480508,0.20917503344531035,0.20744124017788423,0.20715359572476363,0.20532497313011633,0.20456830729481465,0.20301936944957955,0.20149352251859498,0.19995888003076198,0.1994549690585319,0.19876597769494483,0.19817663891709247,0.19592809608498202,0.19480705341148358,0.19293453348638723,0.1920894062254552,0.19126996291726858,0.19118691567898496,0.189308072315591,0.1881907567846643,0.1878653735745919,0.18731811768169654,0.1868450643753242,0.18543199561294563,0.1851040613228291],
#     'TX': [0.446811465719691,0.27737182495245655,0.2316971704373181,0.20464077690155755,0.18646578097133823,0.17257473082541921,0.16334591930022868,0.1542537497636886,0.14858307615717958,0.14232007997765161,0.1376452910618126,0.1328174060518232,0.13084916325887677,0.12703503073104036,0.12325261091684382,0.12075107966241463,0.11894323338343304,0.11721726960533953,0.11631896447001178,0.11348630818352182,0.11098051533424283,0.10875897884138064,0.10726241206452765,0.10674522981524892,0.10512259639199119,0.10448488473099896,0.10301014785958006,0.10174638920650587,0.1009110885189746,0.09910240361748916,0.09746230314634872,0.09713188504602512,0.0964978060675935,0.09516721776908278,0.09427721081748028,0.09334488974247414,0.09333186436671453,0.09202224012446349,0.0913076681863795,0.09037822506150517,0.09027843730567463,0.09009510881111715,0.0892261481978216,0.08876732918310046,0.08779876567446739,0.08782128299476713,0.08586399561819333,0.08583671870604953,0.08547901849018522,0.08568349253446307]
#     }
# 
# lbs = ['Sem Cor', 'Sem Partes', 'Sem Forma', 'Sem Textura', 'Todas', 'Cor', 'Partes', 'Forma', 'Textura'] 
# 
# for i, flag in enumerate(['NCR', 'NPT', 'NSP', 'NTX', 'ALL', 'CR', 'PT', 'SP', 'TX']):  
#     plt.plot(loss[flag], label=lbs[i])
# 
# plt.legend(loc='top right')
# plt.xlabel('Épocas', fontsize=14)
# plt.ylabel('Loss (MSE)', fontsize=14)
# plt.show()