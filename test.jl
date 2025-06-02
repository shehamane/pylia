
abstract type _AAnimal end
mutable struct Animal <: _AAnimal
    __dynamic_attrs::Dict
    _Animal__food_history
    age
    name
    
    function Animal()
        x = new()
        x.__dynamic_attrs = Dict()
        return x
    end
end

function getattr(self::_AAnimal, attr::Symbol)
    if hasproperty(self, attr)
        return getproperty(self, attr)
    elseif haskey(self.__dynamic_attrs, attr)
        return self.__dynamic_attrs[attr]
    else
        throw("Error: No such attribute")
    end
end

function setattr!(self::_AAnimal, attr::Symbol, val)
    if hasproperty(self, attr)
        setproperty!(self, attr, val)
    else
        self.__dynamic_attrs[attr] = val
    end
end

function call(::Val{:__init__}, self::_AAnimal, name, age::Int64)
    setattr!(self, :name, name)
    setattr!(self, :age, age)
    setattr!(self, :_Animal__food_history, [])
    
    return self
end


function call(::Val{:Animal}, ::Val{:__init__}, self, name, age::Int64)
    setattr!(self, :name, name)
    setattr!(self, :age, age)
    setattr!(self, :_Animal__food_history, [])
    
    return self
end


function call(::Val{:_Animal__add_food}, self::_AAnimal, food)
    push!(getattr(self, :_Animal__food_history), food)
end


function call(::Val{:Animal}, ::Val{:_Animal__add_food}, self, food)
    getattr(getattr(self, :_Animal__food_history), :append)
end


function call(::Val{:eat}, self::_AAnimal, food::String)
    call(Val(:_Animal__add_food), self, food)
end


function call(::Val{:Animal}, ::Val{:eat}, self, food::String)
    getattr(self, :_Animal__add_food)
end


function call(::Val{:get_food_history}, self::_AAnimal)
    return getattr(self, :_Animal__food_history)
end


function call(::Val{:Animal}, ::Val{:get_food_history}, self)
    return getattr(self, :_Animal__food_history)
end


animal = call(Val(:__init__), Animal(), "Bobik", 3)

println(animal._Animal__food_history)