# game_of_life
Pythonで作ったコンソール上で動くライフゲーム

## 説明記事
### Pythonで作ったコンソール上で動くライフゲーム
https://qiita.com/y-tetsu/items/264d263717f933ad3cb2

### Pythonで作ったコンソール上で動くライフゲーム#2
https://qiita.com/y-tetsu/items/2db7ce8dd2f8884c2028

## インストール
```
pip install numpy
pip install opencv-python
```

## デモ
### ランダム
<img src="images/random.gif" width="450px">

```
py game_of_life.py
```

### 振動子
#### 八角形
<img src="images/octagon.gif" width="450px">

```
py game_of_life.py octagon
```

#### 銀河
<img src="images/galaxy.gif" width="450px">

```
py game_of_life.py galaxy
```

### 移動物体
#### グライダー
<img src="images/glider.gif" width="450px">

```
py game_of_life.py glider
```

#### 軽量級宇宙船
<img src="images/l-spaceship.gif" width="450px">

```
py game_of_life.py l-spaceship
```

### 繁殖型
#### ブリーダー1
<img src="images/breeder1.gif" width="450px">

```
py game_of_life.py breeder1 -d 2
```

#### ブリーダー2
<img src="images/breeder2.gif" width="450px">

```
py game_of_life.py breeder2 -d 2
```

#### グライダー銃
<img src="images/glider-gun2.gif" width="450px">

```
py game_of_life.py glider-gun -c -w 0.05
```

### 長寿型
#### ダイハード
<img src="images/die-hard.gif" width="450px">

```
py game_of_life.py die-hard
```

#### どんぐり
<img src="images/acorn.gif" width="450px">

```
py game_of_life.py acorn -w 0
```

#### ノアの方舟
<img src="images/noahs-ark2.gif" width="450px">

```
py game_of_life.py noahs-ark -d 0.5 -w 0 -c2
```

### エデンの園配置
#### エデンの園(1971年)
<img src="images/eden1971.gif" width="450px">

```
py game_of_life.py eden1971 -d 2 -w 0.5
```
