CHAMBER DATA CONVERTER
1. Put your .paf files in one folder.
2. (Optional, for haem results) put your fit .csv in the "fits" folder here.
3. Double-click run.bat and answer the questions (Enter accepts the value in [brackets]).
   The first run installs what it needs (internet needed once).
Results: one folder per experiment containing the figure (svg + png) and an Excel workbook
(CcO2, CsO2, VoO2, Events, Metadata). The OD, volume, dilution factor and event labels you type
are saved in the workbook and offered again next time.
Answers are remembered in last_answers.json. A log of each run is in <results>/logs.

To download (Mac/Linux):
git clone https://github.com/bgh512/DePalencify.git
cd DePalencify
chmod +x run.sh run.command
./run.sh

To download (Windows):
git clone https://github.com/bgh512/DePalencify.git
cd DePalencify
chmod +x run.sh run.command
./run.sh
