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

class TypeBase
  def initialize(**kwargs)
    kwargs.each do |k, v|
      instance_variable_set("@#{k}", v)
      self.class.send(:attr_reader, k.to_sym)
    end
  end
end

class TypeC < TypeBase
  class << self
    def is_supported?(obj)
      obj[:type] == 'c'
    end
  end
  def sum
    @child.inject(0){|memo, c|
      memo += c.id
    }
  end
end

class TypeD < TypeBase
  class << self
    def is_supported?(obj)
      obj[:type] == 'd'
    end
  end
  def childid
    @child.id
  end
end

class TypeE < TypeBase
  class << self
    def is_supported?(obj)
      obj[:type] == 'e'
    end
  end
  def upperhobby
    @hobby.upcase
  end
end


class Alter
  class << self
    def regist(klass)
      @@types ||= []
      @@types << klass
    end
  end

  def alter(object)
    case object
    when Hash
      suit_type_klass = @@types.find{|type| type.is_supported?(object) }
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

Alter.regist(TypeC)
Alter.regist(TypeD)
Alter.regist(TypeE)
alter = Alter.new
o = alter.alter(data)

pp o
pp o[2].child[0].id
pp o[2].sum
pp o[3].childid
pp o[4].child.upperhobby
