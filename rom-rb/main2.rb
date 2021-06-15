require "rom"
require "rom/memory"

class Users < ROM::Relation[:memory]
  schema do
    attribute :id, Types::Integer
    attribute :name, Types::String

    primary_key :id

    associations do
      has_many :tasks, combine_key: :user_id, override: true, view: :for_users
    end
  end
end

class Tasks < ROM::Relation[:memory]
  schema do
    attribute :id, Types::Integer
    attribute :user_id, Types::Integer
    attribute :title, Types::String

    primary_key :id
  end

  def for_users(_assoc, users)
    restrict(user_id: users.map { |u| u[:id] })
  end
end

rom = ROM.container(:memory) do |config|
  config.register_relation(Users, Tasks)
end

users = rom.relations[:users]
tasks = rom.relations[:tasks]

[{ id: 1, name: "Jane" }, { id: 2, name: "John" }].each { |tuple| users.insert(tuple) }
[{ id: 1, user_id: 1, title: "Jane's task" }, { id: 2, user_id: 2, title: "John's task" }].each { |tuple| tasks.insert(tuple) }

# load all tasks for all users
tasks.for_users(users.associations[:tasks], users).to_a
# [{:id=>1, :user_id=>1, :title=>"Jane's task"}, {:id=>2, :user_id=>2, :title=>"John's task"}]

# load tasks for particular users
tasks.for_users(users.associations[:tasks], users.restrict(name: "John")).to_a
# [{:id=>2, :user_id=>2, :title=>"John's task"}]

# when we use `combine`, our `for_users` will be called behind the scenes
puts users.restrict(name: "John").combine(:tasks).to_a
# {:id=>2, :name=>"John", :tasks=>[{:id=>2, :user_id=>2