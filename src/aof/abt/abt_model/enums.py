from enum import Enum


class InputSourceType(Enum):
    USER = "user"
    SYSTEM = "system"
    AGENT = "agent"
    SERVICE = "service"


class ActionTargetLocation(Enum):
    IN_PROCESS = "in_process"
    LOCAL_PROCESS = "local_process"
    REMOTE = "remote"


class ActionTargetType(Enum):
    FUNCTION = "function"
    AGENT = "agent"
    MODEL_PROVIDER = "model_provider"
    MCP_PROVIDER = "mcp_provider"
    DATA_STORE = "data_store"
    SERVICE_PROVIDER = "service_provider"
    FILE_SYSTEM = "file_system"


class ActionTargetSubtype(Enum):
    RDBMS = "rdbms"
    KEY_VALUE_DB = "key_value_db"
    DOCUMENT_DB = "document_db"
    VECTOR_DB = "vector_db"
    GRAPH_DB = "graph_db"
    OBJECT_STORE = "object_store"
    SEARCH_ENGINE = "search_engine"
    MESSAGE_BROKER = "message_broker"
    NOTIFICATION_SERVICE = "notification_service"
    PAYMENT_SERVICE = "payment_service"
    POLICY_SERVICE = "policy_service"
    ORDER_SERVICE = "order_service"
    MCP_TOOL = "mcp_tool"
    MCP_PROMPT = "mcp_prompt"
    MCP_RESOURCE = "mcp_resource"
    LOCAL_LLM_RUNTIME = "local_llm_runtime"
    REMOTE_LLM_API = "remote_llm_api"
    EMBEDDING_MODEL = "embedding_model"
    RERANKER_MODEL = "reranker_model"


class ActionInvocationProtocol(Enum):
    FUNCTION_CALL = "function_call"
    HTTP = "http"
    HTTPS = "https"
    MCP = "mcp"
    A2A = "a2a"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    IPC = "ipc"
    STDIO = "stdio"
    KAFKA = "kafka"
    AMQP = "amqp"
    MQTT = "mqtt"


class GuardrailDecision(Enum):
    PASS = "pass"
    FAIL = "fail"
    BLOCK = "block"


class EvaluatorDecision(Enum):
    PASS = "pass"
    FAIL = "fail"
    BLOCK = "block"
