# 数据集说明与版权 (DATASET LICENSE)

本目录存放用于「油田吊装作业安全视频智能分析系统」**演示**的真实现场图片。
图片由后端挂载到 `/static/datasets/`，死数据（违章记录）的 `imageUrl` 指向这些文件。

## 来源

全部图片来自 **Wikimedia Commons**（https://commons.wikimedia.org ），
为公开授权的真实「移动式起重机吊装作业 / 塔吊建筑工地」现场照片，与油田吊装场景在视觉上高度相似。

| 文件 | 主题 | 来源 |
|------|------|------|
| crane_01.jpg | 起重机吊装作业 | Wikimedia Commons（CC 授权） |
| crane_02.jpg | 起重机吊装作业 | Wikimedia Commons（CC 授权） |
| crane_05.jpg | 移动式起重机吊装 | Wikimedia Commons（CC 授权） |
| crane_08.jpg | 移动式起重机吊装预制墙板 | Wikimedia Commons（CC 授权） |
| site_01.jpg ~ site_06.jpg | 塔吊建筑工地 | Wikimedia Commons（CC 授权） |

> 检索方式：Wikimedia Commons MediaWiki API（`action=query&generator=search`），
> 关键词 "mobile crane lifting construction" / "tower crane building site"。

## 许可

Wikimedia Commons 图片通常采用 CC BY / CC BY-SA / 公有领域 等公开许可。
本项目仅用于**学术竞赛演示**，非商业用途。如需商业使用，请逐张到 Commons 文件页核对具体许可与署名要求。

## 说明

- 由于真正「油田现场作业」的公开带标注数据集几乎没有无鉴权直链，本演示采用
  起重机/吊装/工地这类**视觉高度相似**的公开图片替代，足以展示检测框、电子围栏、审核流程等功能。
- 系统中叠加在图片上的检测框（bbox）、电子围栏、置信度为**预置模拟数据**，非对这些图片的真实标注。
- 若本目录为空或图片缺失，后端会自动回退到 `backend-python/app/static/samples/` 下由 PIL 生成的占位图，不影响系统运行。

## 候选数据集（如需扩充真实标注数据）

- SHWD - Safety-Helmet-Wearing-Dataset：https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset （7581 张，安全帽/人员，VOC 标注）
- Dataset Ninja - Safety Helmet and Reflective Jacket：https://datasetninja.com/safety-helmet-and-reflective-jacket （10500 张，PPE，YOLO 标注）
- Roboflow Universe（CC BY 4.0）：Crane-hooks / Tower Crane Component / Construction Site Safety 等
- Kaggle：Hard Hat Detection、Construction Site Safety（需免费账号）

## Added Real Hoisting-Scene Violation Samples

The `aswin_hoist_*.jpg` images under `dataset/images/` come from a real
construction-site safety dataset on Hugging Face:

- Dataset: `aswin00000/ConstructionSiteCleanedDataSet`
- URL: https://huggingface.co/datasets/aswin00000/ConstructionSiteCleanedDataSet
- Format used here: image rows with `rule_*_violation.bounding_box`
- Selected rows: `46`, `1083`, `3008`, `3068`, `3072`

These selected rows contain crane / hoisting / lifting-site context and
non-empty violation bounding boxes. The backend converts the normalized
`bounding_box` values to YOLO-style label files in `dataset/labels/` and then
to pixel boxes for the monitoring-record overlay.

Mapped demo categories:

- rule 1 -> `no_helmet` / `未佩戴安全帽`
- rule 2 -> `no_safety_harness` / `高处作业未系安全带`
- rule 4 -> `person_in_rotation_radius` / `作业人员进入机械旋转半径内`

The selected images are real construction-site images, not AI-generated
SynthSite samples. Their bounding boxes come from the dataset row metadata.

## Added Violation-Labeled PPE Samples

To make monitoring records consistent for the competition demo, the `ppe_*.jpg`
images under `dataset/images/` and matching YOLO labels under `dataset/labels/`
come from a real violation-labeled construction safety dataset:

- Dataset: `LibreYOLO/construction-safety-gsnvb`
- Upstream: Roboflow 100 / Construction Safety Gsnvb
- License: CC-BY-4.0
- Format: YOLO
- Classes: `helmet`, `no-helmet`, `no-vest`, `person`, `vest`
- URL: https://huggingface.co/datasets/LibreYOLO/construction-safety-gsnvb

Only a small number of `test` split samples are used. The backend converts
`no-helmet` and `no-vest` labels into monitoring-record detections and maps
the violation category to the corresponding mock category text.
