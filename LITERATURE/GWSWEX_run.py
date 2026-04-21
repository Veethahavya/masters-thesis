import GWSWEX
import threading
from tqdm import tqdm

#%% Initialize the Class Objects
times = GWSWEX.timing("2020-05-01 00:00:00", "2020-06-01 00:00:00", 3600, 15)

Fort = GWSWEX.Fort("../fortran/", times)

PET = GWSWEX.PET("../data/", times, Fort)

Delft = GWSWEX.Delft("../delft/", times, Fort, prepBC=True, lat_path="SWdis/")

MF6 = GWSWEX.ModFlow("../modflow/", times, Delft, Fort)

RES = GWSWEX.resNC(times, Fort, Delft, MF6)

#%% Define Model Parameters and build the models
PET.prep()
PET.get(throttle=True)

Delft.readNC(lazy=True)
MF6.build(restart=False, res=RES, run=True)

Fort.Ini.n = MF6.Params.sy[0]
Fort.Ini.n_gw = MF6.Params.ss[0]
Fort.Ini.m = 0.3
Fort.Ini.beta = 0.7
Fort.Ini.alpha = 0.15
Fort.Ini.sw_th = 5e-2
Fort.Ini.epv = (Fort.Ini.gok - Fort.Ini.gws)*Fort.Ini.n
Fort.Ini.sm = Fort.Ini.epv*0.8

#%% Initial Model Runs
RES.build()

Fort.build(restart=False, res=RES, run=True)

dRun = threading.Thread(target=Delft.Run, kwargs={"firstRestart":True, "updateTIM":True})
mfRun = threading.Thread(target=MF6.Run, kwargs={"update":True, "err_rerun":True})
dRun.start(); mfRun.start()
dRun.join(); mfRun.join()

Delft.load()
MF6.load()
RES.update(save=True)

#%% Looped Model Runs
for ts in tqdm(range(times.nTS["max"])):
	times.update()
	PET.get(throttle=True)
	Fort.update(Delft, MF6); Fort.Run(); Fort.load()
	dRun = threading.Thread(target=Delft.Run, kwargs={"updateTIM":True})
	mfRun = threading.Thread(target=MF6.Run, kwargs={"update":True, "err_rerun":True})
	dRun.start(); mfRun.start()
	dRun.join(); mfRun.join()
	MF6.load()
	Delft.load()
	RES.update(save=True)
RES.close()