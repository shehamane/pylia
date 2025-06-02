
abstract type _AA end
mutable struct A <: _AA
    __dyn_attrs::Dict
    y
    x
    
    function A()
        return new()
    end
end

function getattr(self::_AA, attr::Symbol)
    if hasproperty(self, attr)
        return getproperty(self, attr)
    elseif haskey(self.__dyn_attrs, attr)
        return self.__dyn_attrs[attr]
    else
        throw("Error")
    end
end

function setattr!(self::_AA, attr::Symbol, val)
    if hasproperty(self, attr)
        setproperty!(self, attr, val)
    else
        self.__dyn_attrs[attr] = val
    end
end

function call(::Val{:__init__}, self::_AA)
    self.__dyn_attrs = Dict()
    self.x = 1
    
    return self
end


function call(::Val{:A}, ::Val{:__init__}, self)
    self.__dyn_attrs = Dict()
    self.x = 1
    
    return self
end


function call(::Val{:bad_style}, self::_AA)
    self.y = 2
end


function call(::Val{:A}, ::Val{:bad_style}, self)
    self.y = 2
end


v = call(Val(:__init__), A())
println(getattr(v, :x))
call(Val(:bad_style), v)
println(getattr(v, :y))
setattr!(v, :z, 3)
println(getattr(v, :z))