drop table if exists clubs;
create table clubs (
  id integer primary key autoincrement,
  uid text not null,
  club_name text not null
);
