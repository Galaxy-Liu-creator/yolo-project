# AegisLift（擎安智吊）· 检测模型训练代码

> 油田吊装作业安全视频智能分析系统 —— **PPE / 着装规范 + 人员违章检测**模型的离线训练流水线。

本目录是系统感知层中 **YOLO 目标检测模型**的训练侧源代码，覆盖「数据校验 → 数据集构建/切分 → 训练 → 评估 → 导出」全流程。它由团队的 YOLOv8 训练工程整理、脱敏、改造而来，统一适配本项目的检测类别与命名约定。

## 与本项目的关系

- 本目录产出的检测权重（`aegislift_ppe_yolov8.pt`）服务于后端的违章识别能力（安全帽、反光衣、人员等）。
- 为保证演示稳定，**后端在线服务采用预置/静态识别结果，运行时不调用本目录脚本**；前后端代码不依赖本目录。本目录作为模型训练侧的完整源码独立留存。
- 数据集样例见仓库 `dataset/`（PPE / 起重机 / 工地现场真实图片，来源见 `dataset/DATASET-LICENSE.md`）。

## 检测类别

数据集采用 5 类（与 `config.py` 的 `CLASS_NAMES`、`data.example.yaml` 一致）：

| ID | 名称 | 含义 |
|----|------|------|
| 0 | `helmet` | 安全帽 |
| 1 | `no-helmet` | 未佩戴安全帽（违章） |
| 2 | `no-vest` | 未穿反光衣（违章） |
| 3 | `person` | 人员 |
| 4 | `vest` | 反光衣 |

## 目录结构

```
train-code/
├─ README.md                       本说明
├─ config.py                       配置中枢：数据路径 / 类别 / 训练默认参 / 产物目录
├─ project_config.example.json     项目化配置模板（覆盖 config.py 默认值）
├─ data.example.yaml               YOLO 数据集定义模板
├─ train.py                        训练总调度 CLI：audit / prepare / train / evaluate / export / all
├─ evaluate_fpfn.py                逐图 FP/FN 评估（IoU 匹配 → precision/recall）
└─ data_tools/                     离线数据工程
   ├─ validate_source.py           数据源体检（图片可读性 + 标签合法性）
   ├─ dataset_tools.py             审计 / 切分 / fullframe & personcrop 数据集落盘
   ├─ build_merged_dataset.py      多源数据合并为带 manifest 的 YOLO 数据集
   └─ generate_split_manifests.py  按数据源均衡的 train/val/holdout 切分
```

## 环境依赖

- Python ≥ 3.9
- [ultralytics](https://github.com/ultralytics/ultralytics)（YOLOv8）、`torch`
- `opencv-python`、`pyyaml`、`numpy`

```bash
pip install ultralytics opencv-python pyyaml numpy
```

## 使用流程

> 所有命令均从 `train-code/` 目录运行。先 `cp project_config.example.json project_config.json` 并按实际数据路径修改。

**1. 数据源体检** —— 检查图片可读性与 YOLO 标签合法性：

```bash
python data_tools/validate_source.py \
    --images datasets/raw/images --labels datasets/raw/labels \
    --num-classes 5 \
    --out-json artifacts/reports/source_check.json \
    --out-md   artifacts/reports/source_check.md
```

**2.（可选）多源合并** —— 把多个数据源按 `*.build.json` 合并成一套数据集：

```bash
python data_tools/build_merged_dataset.py --config datasets/merged_ppe.build.json
```

**3.（可选）均衡切分** —— 按数据源均衡生成 train/val/holdout 清单：

```bash
python data_tools/generate_split_manifests.py \
    --source-manifest artifacts/manifest.csv \
    --output-dir artifacts/splits --holdout-ratio 0.15 --val-ratio 0.15
```

**4. 准备训练集** —— 审计并落盘为 YOLO 目录结构（读 `project_config.json`）：

```bash
python train.py prepare --project-config project_config.json
```

**5. 训练**：

```bash
python train.py train --dataset-yaml data.yaml --name ppe_v1 \
    --epochs 180 --imgsz 640 --batch 16 --device 0
```

**6. 评估** —— 原生指标 + 逐图误报/漏报分析：

```bash
python train.py evaluate --weights artifacts/runs/ppe_v1/weights/best.pt --dataset-yaml data.yaml
python evaluate_fpfn.py  --weights artifacts/runs/ppe_v1/weights/best.pt --data data.yaml --split val
```

**7. 导出** —— 产出可部署权重 `artifacts/export/aegislift_ppe_yolov8.pt`：

```bash
python train.py export --weights artifacts/runs/ppe_v1/weights/best.pt
```

一键串行（prepare → train → evaluate → export）：

```bash
python train.py all --dataset-yaml data.yaml --name ppe_v1
```

各脚本均支持 `-h/--help` 查看完整参数。

## 配置说明

- `config.py` 是配置中枢，集中管理数据根、类别、训练默认参与产物目录；可被 `project_config.json` 覆盖（见 `project_config.example.json`）。
- 仓库内**不含**真实原始数据与权重；`config.py` 中的数据路径为中性占位，请通过 `project_config.json` 或环境变量 `AEGISLIFT_DATA_ROOT` 指向本机数据。
- 训练产物默认写入 `artifacts/`（`prepared/`、`runs/`、`reports/`、`export/`），不纳入版本控制。

## 说明

本目录用于展示团队在检测模型训练侧的完整工程能力。脚本中的数据路径、设备、批大小等均为示例默认值，实际训练请按硬件与数据规模调整。
