function relu(z)
    return max.(0, z)
end

function binary_cross_entropy(y_true, y_pred)
    epsilon = 1e-15
    y_pred = max.(epsilon, min.(1 .- epsilon, y_pred))
    return -mean(y_true .* log.(y_pred) .+ (1 .- y_true) .* log.(1 .- y_pred))
end

function accuracy(y_true, y_pred)
    return mean(y_true .== round.(y_pred))
end

function gradient_descent(X, y, learning_rate, num_iterations)
    m, n = size(X)
    theta = zeros(n)
    for i in 1:num_iterations 
        z = X * theta
        h = relu(z)
        gradient = transpose(X) * (h .- y) ./ m
        theta = theta .- learning_rate .* gradient
        if (i .% 100 .== 0)
            loss = binary_cross_entropy(y, h)
            acc = accuracy(y, h)
        end
    end
    return theta
end
