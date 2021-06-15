data = [
  {
    type: 'a',
    name: 'name1',
  },
  {
    type: 'b',
    tel: '12345',
  },
  {
    type: 'c',
    child: [
      { id: 1},
      { id: 2},
    ]
  },
  {
    type: 'd',
    child: {
      id: 1
    }
  },
  {
    type: 'd',
    child: {
      type: 'e',
      hobby: 'swim'
    }

  }

]

require 'ostruct'


class Alter
  class Types < OpenStruct
    class << self
      attr_reader :types
      def inherited(subclass)
        @types ||= []
        @types << subclass
      end
    end
  end

  def alter(object)
    types = Types.types
    case object
    when Hash
      suit_type_klass = types.find{|type| type.is_supported?(object) }
      if suit_type_klass
        suit_type_klass.new(**Hash[object.map {|k, v| [k, alter(v)] }])
      else
        OpenStruct.new(Hash[object.map {|k, v| [k, alter(v)] }])
      end
    when Array
      object.map {|x| alter(x) }
    else
      object
    end
  end
end


class TypeC < Alter::Types
  class << self
    def is_supported?(obj)
      obj[:type] == 'c'
    end
  end
  def sum
    child.inject(0){|memo, c|
      memo += c.id
    }
  end
end

class TypeD < Alter::Types
  class << self
    def is_supported?(obj)
      obj[:type] == 'd'
    end
  end
  def childid
    child.id
  end
end

class TypeE < Alter::Types
  class << self
    def is_supported?(obj)
      obj[:type] == 'e'
    end
  end
  def upperhobby
    hobby.upcase
  end
end

alter = Alter.new
o = alter.alter(data)

pp o
pp o[2].child[0].id
pp o[2].sum
pp o[3].childid
pp o[4].child.upperhobby
