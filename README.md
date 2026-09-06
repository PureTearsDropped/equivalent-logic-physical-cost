# equivalent-logic-physical-cost

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22486589.svg)](https://doi.org/10.5281/zenodo.22486589)

**等価な論理実装を、実セルの遅延・面積・電力で比べる。** 題材は正確な符号なし 4×4 乗算器。
機能が完全に同じ(256/256 の網羅検証)ネットリスト群を、SkyWater SKY130 の実セル遅延表、OpenSTA、
OpenROAD/LibreLane の配置配線、SDF 付きゲートレベルシミュレーションで比較し、
「全体 DAG のタイミングで決める」最適化器がどこまで効くかを測った記録です。

[English README](README.en.md) · 結果表の全文は [results/summary.md](results/summary.md)

## 何が入っているか

- **タイミングモデル**(`src/`): Liberty の NLDM 表引き(入力遷移 × 出力容量)とスルー伝播を、
  2 入力反転セル(`sky130_timing.py`)から N 入力・非ユネイト・多出力セル(`fullcell.py`)まで一般化。
  30 種の一様変種で OpenSTA と 1.5% 以内で一致。
- **最適化器**: 候補を作るたびに DAG 全体のタイミングを再計算し、臨界遅延が下がる手だけを採用する貪欲法。
  手の種類は ①ゲート複製(シンク集合の分割を列挙) ②drive strength(×1/×2/×4) ③位置ごとの FA/HA/部分積の実装変種。
  どの手も機能等価性を構成的に保ち、最後に網羅検証。
- **物理フロー**(`flow/`): LibreLane 3.0.11 で 11 デザインを配置配線した設定・ネットリスト・結果
  (metrics、STA レポート、SPEF、SDF)。確率電力(`power.py`)とグリッチ込み電力(`sim_power.py`)。
- **原型**(`src/pa4x4.py`, `docs/prototype_notes.md`): 出発点になった、説明用の正規化セル値を使う最適化器。
  本リポは、この原型の主張を実セルで追試するところから始まった。

## 主な結果

配置配線後(SKY130、tt 25°C 1.80 V、配線寄生込み)。エネルギーは 200 MHz ランダム入力、SDF シミュレーション由来。

| 回路 | 遅延 | 論理面積 µm² | 1 演算エネルギー |
|---|---:|---:|---:|
| xor2 二段+a21o の FA(72 セル) | 2290 ps | 430 | **589 fJ** |
| 9-NAND FA、元(124 セル) | 2319 ps | 465 | 749 fJ |
| 全語彙最適化(122 セル) | 2189 ps | 507 | 777 fJ |
| 9-NAND + 複製 12 回(136 セル) | 2207 ps | 510 | 819 fJ |
| 元 + OpenROAD リサイザ(2 ns 目標) | 2252 ps | 807 | 1585 fJ |
| 標準フロー a*b、遅延戦略 2 ns 目標 | 1998 ps | 1775 | 3505 fJ |

分かったこと:

1. **SKY130 では 9-NAND の全加算器が最速。** 専用 fa セル(3323 ps)、xor3+maj3(2795 ps)は大きく遅い。maj3 と xor3 は弱いセル。
2. **全体 DAG 駆動の複製は配線後も残る**(セル遅延で 5.9%、配置配線後 4.8%)。OpenROAD 自身のリサイザは同じ回路で 2252 ps / 807 µm² と、遅延も面積も複製に負け、複製済み回路に掛けると遅くなる。
3. **標準フローは速さ 10% 増を面積 3.5 倍・エネルギー 6 倍で買う。** 面積 600 µm² 以下では手作りネットリストが Pareto 支配。演算器を並べる用途なら同じ面積に 4 個置ける。
4. **OpenSTA の確率的電力見積もりは順位を誤る。** 実測比 1.3〜2.2 倍過大で、しかも倍率が設計ごとに違う。グリッチはトグルの 29〜48%。
5. **語彙を広げても絵は変わらない。** 66 セルを解禁した 2 段貪欲は、NAND だけの複製とほぼ同じ点(2189 ps / 507 µm²)に落ちる。
6. **FPGA では意味を持たない。** yosys/abc は a*b も 3 つのゲート変種も全て 80 LUT・深さ 5 に潰す。8 入力関数は丸ごと再合成される。

## research ブランチ: 算術レベルの等価変形(圧縮スケジュール)

ゲート単位の書き換えではなく、**部分積の列をどの順に圧縮するか**(配列型・Wallace・Dadda・到着時刻貪欲・乱択)を変える。
セルも部分積も同じで、変わるのは加算器のつなぎ方だけ。全スケジュールの正しさは
`lean/ArithEquiv.lean`(core Lean 4、Mathlib 不要、公理は propext と Quot.sound のみ)の定理
`multiplier_correct` が一括で保証し、探索側は候補ごとの証明を持たない。生成したネットリストは従来どおり 256/256 も確認する。

| 回路(配置配線後) | 遅延 | 面積 µm² | 1 演算エネルギー |
|---|---:|---:|---:|
| **Dadda、xor2 二段+a21o(56 セル)** | **1662 ps** | **410** | **440 fJ** |
| Dadda、9-NAND(124 セル) | 1688 ps | 465 | 598 fJ |
| 配列型、9-NAND(124 セル、= 元回路) | 2319 ps | 465 | 749 fJ |
| 標準フロー 2 ns 目標 | 1998 ps | 1775 | 3505 fJ |

同じ 124 セルのまま配列型を Dadda に組み替えるだけで 27% 速くなり、面積代はゼロ。
ゲート複製が面積 10% で 5% を買っていたのとは桁が違う。Dadda+xor2/a21o は標準フローの最速結果に対して
17% 速く、4.3 倍小さく、エネルギー 8 分の 1 で、三軸全部で他の全回路を支配する。
「構造を捨てて関数から再合成する」(abc)のではなく、**算術の構造を保ったまま算術レベルで等価変形する**方が効いた。
詳細は `results/summary.md` §5、再現は `python3 src/arith_search.py 400`。

### 規模を上げる(4 → 32 ビット)

生成器と検証を n ビットに一般化し(`src/scale_sweep.py`)、Lean の定理も任意幅に拡張した
(`multiplier_correct_general`)。探索の計算量は問題にならない: 32×32(1 万セル超)の 1 タイミング評価が純 Python で 0.4 秒、
乱数検証 0.1 秒。規模で変わるのは遅延の在処で、Dadda+リプルの遅延に占める最終加算器の割合が 4 ビット 56%、16 ビット 61%。
最終加算器に Kogge-Stone を足すと 4 ビットでは負け(負荷増)、8 ビットで 12%、16 ビットで 37% 速くなる。
8×8 の配置配線後: 配列 5692 ps → Dadda 3505 ps(同じ 600 セル、エネルギー −36%)→ Dadda+KS 3120 ps。
標準フロー(3 ns 目標)は 3620 ps で面積 3.7 倍、エネルギー 6.3 倍。フローの Booth オプションを有効にしても 3408 ps / 6838 µm² / 10670 fJ で、Dadda+KS に遅延で負け、面積 2.3 倍、エネルギー 14 倍(4 ビットでは Booth は素のフローより全軸で悪い)。表は `results/summary.md` §6。

### total-arith の signed-digit 乗算器への接続

桁を (p,n) の 2 ビットで持つ total-arith-hardware の `sd_mult10` を取り込み(定数畳み込み後 4742 セル)、
同じ生成器で 2 レール(正・負)の borrow-save 乗算器を作って sky130 上で比べた(`src/sd_tree.py`、証明は
`lean/SignedDigit.lean`)。配置配線後・グリッチ込み: 同じ契約(正準桁出力)で 8% 速・面積 2.8 分の 1・エネルギー 2.5 分の 1、
出力を borrow-save で許せば 2.1 倍速・面積 2.5 分の 1(4166 ps / 11241 µm² / 13.8 pJ 対 8659 ps / 27757 µm² / 32.3 pJ)。
毎段で桁を正準に戻す圧縮器(18 ゲート中 8 が正準化)は桁上げを毎段解決するのと同じ代金で、正準化を境界に移すのが carry-save と同じ答え。
表は `results/summary.md` §8。

## 撤回・訂正の記録

途中で言って取り消したことを消さずに残します。

- 原型の「NOR が物理的に高いので all-NAND が勝つ」は、説明用セル値では**セル値だけで決まっていた**(NOR=NAND にすると別の変種が勝つ)。実セルで再計算すると方向は正しかった(nor2_1 の立ち上がり 150 ps 対 nand2_1 82 ps)。
- 原型の「gate-count-only 変種が負ける」理由は NOR の値段ではなく、その FA の cin→carry が 4 段(他は 2 段)という**位相の差**。単位遅延でも負ける。
- 「xor2 系はエネルギーで 19% 損」は確率伝播の誤りで、SDF シミュレーションでは**逆に 21% 得**。撤回。
- 「複製とサイズ変更を組み合わせると最良」はセル遅延だけの話で、配線後は複製単独に負ける。

## 再現手順

```
pip install -r requirements.txt          # numpy のみ
python3 src/audit.py                     # 原型の追試と混同の切り分け(外部ツール不要)
python3 src/sky130_timing.py             # 実セル NLDM での 3 変種と貪欲複製(外部ツール不要)
sh lib/fetch_lib.sh                      # 完全 Liberty(13 MB、Apache-2.0)を取得
export STA=/path/to/sta                  # OpenSTA 実行ファイル
python3 src/fullcell.py                  # 一様 30 変種、模型 vs OpenSTA
python3 src/optimize_full.py             # 全語彙 2 段貪欲
python3 src/sizing.py                    # 複製 vs drive strength
python3 flow/summary.py                  # 配置配線結果の表(同梱の結果から)
python3 flow/power.py                    # 確率電力
export PDK_VERILOG=/path/to/sky130A/libs.ref/sky130_fd_sc_hd/verilog
python3 flow/sim_power.py 32768          # SDF シミュレーション+VCD 電力(iverilog 必要)
```

配置配線をやり直すには LibreLane(Nix で `nix shell github:librelane/librelane`)を入れ、
`flow/designs/<name>/` で `librelane config.json` を実行します。

構造ネットリストを LibreLane に通すときの罠(全部踏みました):

- `SYNTH_ELABORATE_ONLY` で合成を素通しし、リサイザ類(`RUN_POST_*_REPAIR`、`*_RESIZER_*`)を全部切る。
- Verilog は wire を全宣言し、`assign` を使わずポートをピンに直結する。
- クロック無しの組合せ回路はダミークロック扱いになる。`CLOCK_UNCERTAINTY_CONSTRAINT` を 0 にしないとホールド違反で止まり、基準側ではホールド修正バッファが挿入されて面積が膨らむ。
- 遅延は `stapostpnr/.../max.rpt` の data arrival time で読む(ws は不確かさ込み)。
- OpenSTA を子プロセスで呼ぶときは stdin を閉じる。閉じないと対話待ちで固まる。
- iverilog は `-gspecify` を付けないと SDF を黙って無視する(全遷移がクロック格子上に乗る)。
  電源ピン無しセルモデルは `-gspecify` で elaborate に失敗する(未使用の lpflow_bleeder が VPWR を参照)ので、
  電源付きネットリスト(`*.pnl.v`)と `-DUSE_POWER_PINS` を使う。

## 制限

- 4×4 の 1 位相のみ。配列の接続は固定で、探索は FA/HA の中身・複製・サイズだけ。
- 探索は単一手の貪欲で、停滞手・先読み・バッファ挿入が無い。標準フローとの差(面積を使って速くする側)はこの探索の限界。
- tt コーナーのみ。入力は駆動セル 1 種、出力負荷 10 fF 固定。
- エネルギーはランダム入力の平均。実シリコンでの測定はしていない。
- 新規性は主張しない。全体 DAG のタイミング駆動最適化も NLDM も既知の技術で、ここにあるのは「実セルと実フローで測った記録」。

## 構成

```
src/        タイミングモデル・最適化器・監査スクリプト
cells/      SKY130 セル別 Liberty(JSON、Apache-2.0)と面積表
flow/       LibreLane 設定とネットリスト(designs/)、配置配線結果(results/)、電力スクリプト
results/    結果表(summary.md)と探索ログ
docs/       原型の解説
lib/        完全 Liberty の取得スクリプト(ファイルは非同梱)
```

## ライセンス

コードと文書は 0BSD。`cells/` の Liberty 由来データは SkyWater PDK の Apache-2.0(`cells/NOTICE`)。
