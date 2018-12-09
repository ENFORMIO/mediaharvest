create table article_extract (
    id bigint(20) not null primary key auto_increment,
    version int not null default 0,
    title varchar(250) default null
);

describe article_extract;
