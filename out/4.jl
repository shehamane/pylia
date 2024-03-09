function pow(x::Int64, y::Int64)::Int64
    if (y .== 0)
        return 1
    end
    return x .* pow(x, y .- 1)
end

function fibb(n::Int64)::Int64
    if (n .== 0)
        return 0
    end
    if (n .== 1)
        return 1
    end
    return fibb(n .- 1) .+ fibb(n .- 2)
end

function inverse(x::Float64)::Float64
    return 1 ./ x
end

println(pow(2, 5))
println(fibb(14))
println(inverse(3.14))