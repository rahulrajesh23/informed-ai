from enum import Enum


class LogCategory(Enum):
    WEB_APP = "web_app"
    QUERY = "query"
    CHAT = "chat"
    FEEDBACK = "feedback"
    INVESTIGATION = "investigation"
    BOOTSTRAP = "bootstrap"
    SERVICE_MAP = "service_map"
    MEMORY_STORE = "memory_store"
    INDEX = "index"
    EXTRACTORS = "extractors"
    SLACK = "slack"
    CACHE = "cache"
    TOOL = "tool"
    CONFIG = "config"
    SYSTEM = "system"
    SLACK_COMMS_AUDIT = "slack_comms_audit"
    LLM_TRACE = "llm_trace"
    DEMO = "demo"


class LogSubCategory(Enum):
    READY = "ready"
    CONFLUENCE = "confluence"
    K8S = "k8s"
    GITHUB = "github"
    MENTION = "mention"
    CHANNEL_MESSAGE = "channel_message"
    DIRECT_MESSAGE = "direct_message"
    MESSAGE_SKIPPED = "message_skipped"
    NEW = "new"
    TOTAL = "total"
    STATS = "stats"
    ACTION = "action"
    LLM_UNIT_COST = "llm_unit_cost"
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    LLM_USAGE = "llm_usage"
    EMBEDDINGS = "embeddings"
    DELETED = "deleted"
    PLANNING = "planning"
    RETRIEVAL = "retrieval"
    EXECUTION = "execution"
    REFLECTION = "reflection"
    MEMORY = "memory"
    VECTOR_STORE = "vector_store"
    REMOTE_CONFIG_CHANGE = "remote_config_change"
    EXTRACTION = "extraction_job"
    UNHANDLED_SLACK_EVENT = "unhandled_slack_event"


class LogEvent(Enum):
    MESSAGE_EVENT = "message_event"
    MESSAGE_FEEDBACK_EVENT = "message_feedback_event"
    QUERY_EVENT = "query_event"
    CHAT_LABEL_EVENT = "chat_label_event"
    CHAT_THREAD_CREATED_EVENT = "chat_event"
    CHAT_THREAD_COMPLETED_EVENT = "chat_thread_completed_event"
    CHAT_THREAD_REVIEWED_EVENT = "chat_thread_reviewed_event"
    CHAT_THREAD_ARCHIVED_EVENT = "chat_thread_archived_event"


class LogState(Enum):
    START = "start"
    END = "end"


class LogType(Enum):
    BACKGROUND = "background"


class LogLevels(Enum):
    """
    Custom log levels for Cleric in addition to the standard ones.
    """

    DIAGNOSTIC = 27  # Log level between severity of success and warning
