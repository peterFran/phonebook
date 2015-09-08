drop table if exists phonebook;
create table phonebook (
  id integer primary key autoincrement,
  forename text not null,
  surname text not null,
  telephone text not null,
  address text not null
);