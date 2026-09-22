# 基金智能监控雷达 PRO MAX V9.1.1 Web

这是可直接部署到 Streamlit Community Cloud 的网页版基金监控工具。

## 部署
1. 把本目录全部文件上传到 GitHub 仓库。
2. 打开 https://share.streamlit.io/，用 GitHub 登录。
3. Create app → Yup, I have an app。
4. 选择仓库、main 分支、`app.py`。
5. Deploy。

## 说明
- 不需要本地 Python、bat 文件或 CMD。
- 115 只基金名单内置在 `app.py`。
- 数据获取失败会自动重试，并对 ETF 使用备用数据源。
- GitHub 中修改代码后，Streamlit Community Cloud 会自动更新部署。
- 信号仅作技术分析辅助，不构成投资建议。
