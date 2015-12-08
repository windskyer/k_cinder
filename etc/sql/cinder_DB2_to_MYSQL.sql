drop table if exists ibm_hmcs;

drop table if exists ibm_hmc_clusters;

drop table if exists onboard_tasks;

drop table if exists onboard_task_volumes;

drop table if exists storage_nodes;

drop table if exists storage_node_health_status;

drop table if exists volume_health_status;

drop table if exists volume_restricted_metadata;


/*==============================================================*/
/* table: ibm_hmcs                                              */
/*==============================================================*/
create table ibm_hmcs
(
   created_at           timestamp,
   updated_at           timestamp,
   deleted_at           timestamp,
   deleted              smallint,
   id                   int not null auto_increment,
   uuid                 varchar(36) not null,
   display_name         varchar(255) not null,
   access_ip            varchar(255) not null,
   user_id              varchar(63) not null,
   user_credentials     varchar(255) not null,
   registered_at        timestamp,
   primary key (id),
   check (deleted in (0, 1))
);

/*==============================================================*/
/* table: ibm_hmc_clusters                                      */
/*==============================================================*/
create table ibm_hmc_clusters
(
   created_at           timestamp,
   updated_at           timestamp,
   deleted_at           timestamp,
   deleted              smallint,
   id                   int not null auto_increment,
   hmc_uuid             varchar(36) not null,
   host_name            varchar(255) not null,
   primary key (id),
   check (deleted in (0, 1))
);

/*==============================================================*/
/* table: onboard_tasks                                         */
/*==============================================================*/
create table onboard_tasks
(
   created_at           timestamp,
   updated_at           timestamp,
   deleted_at           timestamp,
   deleted              smallint,
   id                   int not null auto_increment,
   host                 varchar(255) not null,
   status               varchar(31),
   started_at           timestamp,
   ended_at             timestamp,
   progress             int,
   primary key (id),
   check (deleted in (0, 1))
);

/*==============================================================*/
/* table: onboard_task_volumes                                  */
/*==============================================================*/
create table onboard_task_volumes
(
   created_at           timestamp,
   updated_at           timestamp,
   deleted_at           timestamp,
   deleted              smallint,
   id                   int not null auto_increment,
   task_id              int not null,
   volume_uuid          varchar(36) not null,
   volume_name          varchar(255) not null,
   status               varchar(31) not null,
   fault_message        varchar(255),
   primary key (id),
   check (deleted in (0, 1))
);

/*==============================================================*/
/* table: storage_nodes                                         */
/*==============================================================*/
create table storage_nodes
(
   created_at           timestamp,
   updated_at           timestamp,
   deleted_at           timestamp,
   deleted              smallint,
   id                   int not null auto_increment,
   service_id           int not null,
   storage_hostname     varchar(255) not null,
   backend_state        varchar(31),
   backend_type         varchar(31),
   backend_id           varchar(255),
   total_capacity_gb    float,
   free_capacity_gb     float,
   volume_count         int,
   primary key (id),
   check (deleted in (0, 1))
);

/*==============================================================*/
/* table: storage_node_health_status                            */
/*==============================================================*/
create table storage_node_health_status
(
   created_at           timestamp,
   updated_at           timestamp,
   deleted_at           timestamp,
   deleted              smallint,
   id                   varchar(36) not null,
   health_state         varchar(31),
   reason               TEXT,
   unknown_reason_details TEXT,
   primary key (id),
   check (deleted in (0, 1))
);

/*==============================================================*/
/* table: volume_health_status                                  */
/*==============================================================*/
create table volume_health_status
(
   created_at           timestamp,
   updated_at           timestamp,
   deleted_at           timestamp,
   deleted              smallint,
   id                   varchar(36) not null,
   health_state         varchar(31),
   reason               TEXT,
   unknown_reason_details TEXT,
   primary key (id),
   check (deleted in (0, 1))
);

/*==============================================================*/
/* table: volume_restricted_metadata                            */
/*==============================================================*/
create table volume_restricted_metadata
(
   created_at           timestamp,
   updated_at           timestamp,
   deleted_at           timestamp,
   deleted              smallint,
   id                   int not null auto_increment,
   `key`                varchar(255),
   value                varchar(255),
   volume_id            varchar(36) not null,
   primary key (id),
   check (deleted in (0, 1))
);
