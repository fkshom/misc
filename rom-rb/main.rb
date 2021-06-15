require 'rom-repository'
require 'rom-yaml'
require 'pry'

path = './sample.yaml'
configuration = ROM::Configuration.new(:yaml, path)
# rom = ROM.container(configuration) do |config|
# rom = ROM::Configuration.new(:yaml, path) do |config|

# end
class Users < ROM::Relation[:yaml]
  schema(infer: true) do
    # attribute :unko, Types::String.optional, alias: :clean
    attribute :id, Types::Integer
    primary_key :id
  end
  auto_struct true
end
configuration.register_relation(Users)

class Tasks < ROM::YAML::Relation
  schema(:tasks, infer: true) do
    attribute :id, Types::Integer
    primary_key :id
    attribute :user_id, Types::Integer
  end
  auto_struct true
end
configuration.register_relation(Tasks)

container = ROM.container(configuration) do |config|
  config.register_relation(Users, Tasks)
end



class UserRepo < ROM::Repository[:users]
end
class TaskRepo < ROM::Repository[:tasks]
end

urepo = UserRepo.new(container)
trepo = TaskRepo.new(container)
binding.pry
