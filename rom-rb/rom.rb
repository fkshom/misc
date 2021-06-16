require 'dry-types'
require 'dry-struct'


module Types
  include Dry.Types()
end

module Store
  module Loader
    def load_from_hash(obj)
        @items ||= []
        @items << self.new(**obj)
    end
  end

  class VirtualMachine < Dry::Struct
    extend Loader
    class << self
      def by_id(id)
        @items.select{|item| item.id == id}
      end
    end

    class SubMachine < Dry::Struct
      transform_keys(&:to_sym)
      attribute :id, Types::Integer
    end
    transform_keys(&:to_sym)
    attribute :id, Types::Integer
    attribute :child, Dry::Struct do
      transform_keys(&:to_sym)
      attribute :id, Types::Integer
    end
    attribute :submachine, SubMachine
    attribute? :non, Types::String
    attribute :opt, Types::String.optional
  end
end

data = {
  id: 1,
  child: {
    id: 2
  },
  submachine: {
    id: 3
  },
  opt: nil
}

pp Store::VirtualMachine.load_from_hash(data)
