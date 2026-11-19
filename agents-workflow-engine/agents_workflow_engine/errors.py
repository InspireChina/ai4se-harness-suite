"""图的加载、合并、校验、渲染与运行共用的错误。"""


class GraphError(Exception):
    """图不合法或跑不下去。消息里写明节点、原因和下一步。"""


class NeedInput(GraphError):
    """图停在人的节点上，进度已记下。"""
