require_relative 'logger'

class Calculator
  def add(a, b)
    result = a + b
    Logger.log("Adding #{a} and #{b} = #{result}")
    result
  end
end
