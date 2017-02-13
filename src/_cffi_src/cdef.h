typedef struct { ...; } posix_spawnattr_t;
typedef struct { ...; } posix_spawn_file_actions_t;
typedef int pid_t;
typedef unsigned int mode_t;
typedef ... sigset_t;

int posix_spawn(pid_t *, const char *,
        const posix_spawn_file_actions_t *,
        const posix_spawnattr_t *,
        char *const __argv[],
        char *const __envp[]);

int posix_spawnp(pid_t *, const char *,
        const posix_spawn_file_actions_t *,
        const posix_spawnattr_t *,
        char *const __argv[],
        char *const __envp[]);

int posix_spawn_file_actions_addclose(posix_spawn_file_actions_t *, int);
int posix_spawn_file_actions_adddup2(posix_spawn_file_actions_t *, int, int);
int posix_spawn_file_actions_addopen(
        posix_spawn_file_actions_t *, int,
        const char *, int, mode_t);
int posix_spawn_file_actions_destroy(posix_spawn_file_actions_t *);
int posix_spawn_file_actions_init(posix_spawn_file_actions_t *);

int posix_spawnattr_destroy(posix_spawnattr_t *);
int posix_spawnattr_getsigdefault(const posix_spawnattr_t *,
        sigset_t *);
int posix_spawnattr_getflags(const posix_spawnattr_t *,
        short *);
int posix_spawnattr_getpgroup(const posix_spawnattr_t *,
        pid_t *);
int posix_spawnattr_getsigmask(const posix_spawnattr_t *,
        sigset_t *);
int posix_spawnattr_init(posix_spawnattr_t *);
int posix_spawnattr_setsigdefault(posix_spawnattr_t *,
        const sigset_t *);
int posix_spawnattr_setflags(posix_spawnattr_t *, short);
int posix_spawnattr_setpgroup(posix_spawnattr_t *, pid_t);
int posix_spawnattr_setsigmask(posix_spawnattr_t *,
        const sigset_t *);
