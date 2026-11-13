# 162 份大型数据清单的私有备份

这里保存 audio-driven-v5 和 audio-driven-v5-data-processing 两个项目此前因超过 100 MB 而未上传的全部 **162 份数据清单**。原始大小 **179,885,025,283 字节**，无损压缩后 **20,362,189,198 字节**，分为 **174 个数据附件**。

实际数据保存在本仓库的 [Release 附件](https://github.com/li-qi-lin/audio-driven-v5-large-manifests-backup/releases/tag/large-manifests-20261113) 中。原始路径、大小、SHA-256 以及每个分片的校验值见 `large_manifests.json`，最终上传校验结果见 `verification.json`。上传期间 Release 是草稿；最终状态见 `summary.json`。

此前完成的代码、配置、文档和小清单备份仍在另一个账号的[原仓库](https://github.com/liqilin-eudaemonia/audio-driven-v5-data-processing/tree/backup-20261113-155045)。本仓库只补充这 162 个大清单，两边私有仓库的访问权限分别管理。

## 下载、校验及恢复

先以具有本仓库访问权限的 GitHub 账号登录 `gh`，然后执行：

```bash
gh release download large-manifests-20261113 --repo li-qi-lin/audio-driven-v5-large-manifests-backup --dir large-manifest-download
cd large-manifest-download
python3 restore_large_manifests.py --parts-dir . --verify-only
python3 restore_large_manifests.py --parts-dir . --destination /path/to/restore-root
```

恢复目录下会创建两个原项目同名目录并写回原始相对路径。可以在代码备份恢复完成后，将这些大清单恢复到同一个目录。已有且内容不同的文件不会覆盖。恢复程序会验证所有分片和每个原始文件的 SHA-256；本次保存的是各文件打包时的版本，生产任务后续更新不会自动同步。

其他音视频、模型权重、环境和缓存仍按此前约定保留原位置。本备份没有修改原项目目录。
