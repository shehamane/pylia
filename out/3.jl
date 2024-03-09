function main()
    x = [1, 2, (2 .+ 2 .* 2)]
    y::Float64 = 1e-16
    println(x .+ y)
end

for i in 1:10 
    main()
end