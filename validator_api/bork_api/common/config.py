# coding=utf-8
import os
from oslo_config import cfg

CONF = cfg.CONF
# General Options
opts = [
    cfg.StrOpt('bind_host', default='0.0.0.0'),
    cfg.PortOpt('bind_port', default=9292),
]
CONF.register_opts(opts)

# Chef options
opts = [
    cfg.StrOpt('cmd_install', default='knife cookbook site install {}'),
    cfg.StrOpt('cmd_config', default='{"run_list": [ "recipe[%s]"]}'),
    cfg.StrOpt('cmd_inject', default="echo '{}' >/etc/chef/solo.json"),
    cfg.StrOpt('cmd_syntax', default='knife cookbook test {}'),
    cfg.StrOpt('cmd_deploy', default='chef-solo –c /etc/chef/solo.rb -j /etc/chef/solo.json'),
]
CONF.register_opts(opts, group="clients_chef")

# Keystone options
CONF.register_opt(cfg.StrOpt('auth_uri', default="http://cloud.lab.fiware.org:4730/v2.0"), group="keystone_authtoken")

# Docker options
opts = [
    cfg.StrOpt('url', default="tcp://127.0.0.1:2375"),
    cfg.StrOpt('build_dir', default="/etc/bork_api")
]
CONF.register_opts(opts, group="clients_docker")

# Puppet options
opts = [
    cfg.StrOpt('cmd_install', default='puppet module install {}'),
    cfg.StrOpt('cmd_syntax', default='puppet parser validate {}'),
    cfg.StrOpt('cmd_deploy', default='puppet apply --modulepath=./modules -e "class { \'%s\':}" --debug'),
]
CONF.register_opts(opts, group="clients_puppet")

# Local storage options
opts = [
    cfg.StrOpt('local_path', default=r"/tmp/cookbooks"),
]
CONF.register_opts(opts, group="clients_storage")

# Git repo options
opts = [
    cfg.StrOpt('repo_path', default=r"/opt/cookbooks"),
]
CONF.register_opts(opts, group="clients_git")

# Logging options
common_cli_opts = [
    cfg.BoolOpt('debug',
                short='d',
                default=False,
                help='Print debugging output (set logging level to '
                     'DEBUG instead of default WARNING level).'),
    cfg.BoolOpt('verbose',
                short='v',
                default=False,
                help='Print more verbose output (set logging level to '
                     'INFO instead of default WARNING level).'),
]
_DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging_cli_opts = [
    cfg.StrOpt('log-config-append',
               metavar='PATH',
               deprecated_name='log-config',
               help='The name of a logging configuration file. This file '
                    'is appended to any existing logging configuration '
                    'files. For details about logging configuration files, '
                    'see the Python logging module documentation.'),
    cfg.StrOpt('log-format',
               metavar='FORMAT',
               help='DEPRECATED. '
                    'A logging.Formatter log message format string which may '
                    'use any of the available logging.LogRecord attributes. '
                    'This option is deprecated.  Please use '
                    'logging_context_format_string and '
                    'logging_default_format_string instead.'),
    cfg.StrOpt('log-date-format',
               default=_DEFAULT_LOG_DATE_FORMAT,
               metavar='DATE_FORMAT',
               help='Format string for %%(asctime)s in log records. '
                    'Default: %(default)s .'),
    cfg.StrOpt('log-file',
               metavar='PATH',
               deprecated_name='logfile',
               help='(Optional) Name of log file to output to. '
                    'If no default is set, logging will go to stdout.'),
    cfg.StrOpt('log-dir',
               deprecated_name='logdir',
               help='(Optional) The base directory used for relative '
                    '--log-file paths.'),
    cfg.BoolOpt('use-syslog',
                default=False,
                help='Use syslog for logging. '
                     'Existing syslog format is DEPRECATED during I, '
                     'and will change in J to honor RFC5424.'),
    cfg.BoolOpt('use-syslog-rfc-format',
                # TODO(bogdando) remove or use True after existing
                #    syslog format deprecation in J
                default=False,
                help='(Optional) Enables or disables syslog rfc5424 format '
                     'for logging. If enabled, prefixes the MSG part of the '
                     'syslog message with APP-NAME (RFC5424). The '
                     'format without the APP-NAME is deprecated in I, '
                     'and will be removed in J.'),
    cfg.StrOpt('syslog-log-facility',
               default='LOG_USER',
               help='Syslog facility to receive log lines.')
]

generic_log_opts = [
    cfg.BoolOpt('use_stderr',
                default=True,
                help='Log output to standard error.')
]

DEFAULT_LOG_LEVELS = ['amqp=WARN', 'amqplib=WARN', 'boto=WARN',
                      'qpid=WARN', 'sqlalchemy=WARN', 'suds=INFO',
                      'oslo.messaging=INFO', 'iso8601=WARN',
                      'requests.packages.urllib3.connectionpool=WARN',
                      'urllib3.connectionpool=WARN', 'websocket=WARN',
                      "keystonemiddleware=WARN", "routes.middleware=WARN",
                      "stevedore=WARN"]

log_opts = [
    cfg.StrOpt('logging_context_format_string',
               default='%(asctime)s.%(msecs)03d %(process)d %(levelname)s '
                       '%(name)s [%(request_id)s %(user_identity)s] '
                       '%(instance)s%(message)s',
               help='Format string to use for log messages with context.'),
    cfg.StrOpt('logging_default_format_string',
               default='%(color)s%(asctime)s.%(msecs)03d %(process)d %(levelname)s '
                       '%(name)s [-] %(instance)s%(message)s',
               help='Format string to use for log messages without context.'),
    cfg.StrOpt('logging_debug_format_suffix',
               default='%(funcName)s %(pathname)s:%(lineno)d',
               help='Data to append to log format when level is DEBUG.'),
    cfg.StrOpt('logging_exception_prefix',
               default='%(asctime)s.%(msecs)03d %(process)d TRACE %(name)s '
                       '%(instance)s',
               help='Prefix each line of exception output with this format.'),
    cfg.ListOpt('default_log_levels',
                default=DEFAULT_LOG_LEVELS,
                help='List of logger=LEVEL pairs.'),
    cfg.BoolOpt('publish_errors',
                default=False,
                help='Enables or disables publication of error events.'),
    cfg.BoolOpt('fatal_deprecations',
                default=False,
                help='Enables or disables fatal status of deprecations.'),

    # NOTE(mikal): there are two options here because sometimes we are handed
    # a full instance (and could include more information), and other times we
    # are just handed a UUID for the instance.
    cfg.StrOpt('instance_format',
               default='[instance: %(uuid)s] ',
               help='The format for an instance that is passed with the log '
                    'message.'),
    cfg.StrOpt('instance_uuid_format',
               default='[instance: %(uuid)s] ',
               help='The format for an instance UUID that is passed with the '
                    'log message.'),
]
CONF.register_cli_opts(common_cli_opts)
CONF.register_cli_opts(logging_cli_opts)
CONF.register_opts(generic_log_opts)
CONF.register_opts(log_opts)


def setup_config(app):
    conf_file = "/etc/bork_api/%s.conf" % app
    if not os.path.exists(conf_file):
        conf_file = "../etc/bork_api/%s.conf" % app
    CONF(project=app, args=["--config-file=%s" % conf_file], default_config_files=[conf_file])

