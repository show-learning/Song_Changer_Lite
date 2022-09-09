# Readme

執行環境：python3.8

載好相關套件後,執行test_main.py即可執行（需有PYQT5,numpy,spleeter等）

若轉換失敗,可以試著去change中調大frame_size的大小（預設2^14）,但會影響相似度

若音檔無法播放,可以試著線上轉mp3再播出

歌曲必須放在同一層目錄才能執行

第一行選擇歌曲

第二行輸入副歌的秒數

輸出副歌：chrous.wav

第三行選擇想轉換的聲音（限wav檔）,會產生data.txt,紀錄取樣的資料,並產生sound.wav作為合成出的範例

輸出結果：output.wav和多了伴奏的plus.wav

若不想用UI可以改執行sample_fade內的scl.py

另有plus版,是把伴奏合回去的結果

spleeter能將歌曲的背景與人聲分離

需要spleeter是因為我們試過直接進行替換的效果並不使很好,因此選擇只替換人聲的部分

執行想法:

1.切副歌(使用pychrous) 

2.將副歌拿去spleeter切出vocal和accomplish (使用spleeter)

3.取樣音檔,取得合成的資料(產生sound.wav檔)

4.將切出來的vocal拿去做替換 輸出output.wav檔

5.將替換完的檔案與accomplish疊合 輸出plus.wav檔



Credit:

副歌擷取：python-pychrous https://towardsdatascience.com/finding-choruses-in-songs-with-python-a925165f94a8

https://github.com/vivjay30/pychorus

聲音分離：spleeterhttps://github.com/deezer/spleeter

音檔替換:https://kanido386.github.io/2020/09/summer-project/

窗函數:https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.get_window.html