# -*- coding: utf-8 -*-
"""AegisLift（擎安智吊）训练数据工具子包。

汇集离线数据工程脚本，服务于 PPE / 着装规范检测模型的数据准备：

- ``validate_source``        数据源体检（图片可读性 + YOLO 标签合法性）
- ``dataset_tools``          数据审计 / 序列切分 / fullframe & personcrop 数据集落盘
- ``build_merged_dataset``   多源数据合并为带 split-manifest 的 YOLO 数据集
- ``generate_split_manifests``  按数据源均衡的 train / val / holdout 切分
"""
