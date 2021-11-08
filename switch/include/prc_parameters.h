#define DEFAULT_PRC_DIR "romfs:/Config"
#define PRC_PATTERNS "*.prc"
#define PRC_ENCRYPTED_PATTERNS ""
#define PRC_EXECUTABLE_PATTERNS ""
#define PRC_PUBLIC_KEYS_FILENAME ""

// Environment variables are not available for Switch
#define PRC_DIR_ENVVARS ""
#define PRC_EXECUTABLE_ARGS_ENVVAR ""
#define PRC_PATH2_ENVVARS ""
#define PRC_PATH_ENVVARS ""

// Encryption is not available until we have openssl
#define PRC_ENCRYPTION_KEY ""

// Trust levels
#define PRC_DCONFIG_TRUST_LEVEL 0
#define PRC_RESPECT_TRUST_LEVEL 0
#define PRC_INC_TRUST_LEVEL 0