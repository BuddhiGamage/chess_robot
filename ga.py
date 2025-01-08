import numpy as np
import random
import cv2
import pytesseract

# Define the target array
target_array = [
    [1, 1, 1, 1, 1, 1, 1, 'F'],
    [1, 1, 'L', 1, 'F', 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 'P', 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 'F', 1, 'P', 1, 1, 1],
    [1, 'F', 1, 'N', 1, 1, 1, 'X'],
    ['T', 1, 1, 1, 1, 1, 1, 1]
]
image_path='/home/buddhi/Projects/chess_robot/extracted_chessboard.jpg'

# Preprocess the image
def preprocess_image(img,x,y):
    
   # Convert the image to an 8-bit unsigned integer type
    gray = np.uint8(img * 255)
    
    gray_inv = cv2.bitwise_not(gray)

    binary = cv2.adaptiveThreshold(gray_inv,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,x,y)
    
    return binary

# Placeholder function for chessboard_to_matrix
def chessboard_to_matrix(img,i,j):
    """
    Converts a chessboard image with letters to an 8x8 matrix.

    Args:
        image_path: Path to the chessboard image.

    Returns:
        An 8x8 NumPy array representing the chessboard, 
        where '1' represents empty squares and letters represent 
        squares with corresponding letters.
    """
    
    # Constants
    image_size = 800  # Image dimensions (assume square image)  
    top_border = 38  # Top border width in pixels
    bottom_border = 38  # Bottom border width in pixels
    left_border = 37  # Left border width in pixels
    right_border = 35  # Right border width in pixels
    num_squares = 8  # Number of squares per row/column
    square_width = (image_size - left_border - right_border) // num_squares
    square_height = (image_size - top_border - bottom_border) // num_squares
    extra_boundary = 10  # Additional boundary in pixels
    
    # Resize the image to ensure it's 800x800
    img = cv2.resize(img, (image_size, image_size))

    # Preprocess the image
    preprocessed_image = preprocess_image(img,i,j)

    
    
    # Create an empty 8x8 matrix
    matrix = np.zeros((8, 8), dtype=object)

    # Iterate through each square
    for row in range(num_squares):
        for col in range(num_squares):
            # Adjust coordinates for the top and bottom halves based on the borders
            if row < num_squares // 2:
                start_y = top_border + row * square_height
                end_y = start_y + square_height
            else:
                start_y = (image_size - bottom_border) - (num_squares - row) * square_height
                end_y = start_y + square_height

            # Adjust coordinates for the left and right halves based on the borders
            if col < num_squares // 2:
                start_x = left_border + col * square_width
                end_x = start_x + square_width
            else:
                start_x = (image_size - right_border) - (num_squares - col) * square_width
                end_x = start_x + square_width
                
            # Adjust the rectangle to include an additional pixel boundary
            adjusted_start_x = max(start_x - extra_boundary, 0)
            adjusted_start_y = max(start_y - extra_boundary, 0)
            adjusted_end_x = min(end_x + extra_boundary, image_size)
            adjusted_end_y = min(end_y + extra_boundary, image_size)

            # # Extract the ROI of the square
            roi = preprocessed_image[adjusted_start_y:adjusted_end_y, adjusted_start_x:adjusted_end_x]

            letter = pytesseract.image_to_string(roi, config='--psm 10 -c tessedit_char_whitelist=TLXEMFRNBKQP')
            letter = letter.strip()

            # Append detected letter or '1' for empty square
            if letter:
                matrix[row][col] = letter
            else:
                matrix[row][col] = 1

    return matrix

# Fitness function: measures how close a generated matrix is to the target array
def fitness(individual):
    x, y = individual
    chessboard_matrix = chessboard_to_matrix(img, x, y)
    score = 0
    for i in range(len(chessboard_matrix)):
        for j in range(len(chessboard_matrix[i])):
            if(target_array[i][j]==1):
                if chessboard_matrix[i][j]!=1:
                    score-=1
            elif isinstance(chessboard_matrix[i][j], str) and chessboard_matrix[i][j] == target_array[i][j]:
                score += 1  # Increment score for matching letters
    
    return score

# Selection function: selects two parents from the population based on fitness
def select_parents(population, fitness_scores,target_max):

    probabilities = [f / target_max if f >= 0 else 0 for f in fitness_scores] # 0 for negative fitness
    parents = random.choices(population, weights=probabilities, k=2)
    return parents

# Crossover function: combines two parents to create an offspring
def crossover(parent1, parent2):
    crossover_point = random.randint(1, 2)  # As we have two variables: x and y
    if crossover_point == 1:
        return (parent1[0], parent2[1])
    else:
        return (parent2[0], parent1[1])

# Mutation function: randomly mutates one of the parents' values
def mutate(individual, mutation_rate=0.1):
    if random.random() < mutation_rate:
        x, y = individual
        # Ensure x is always odd
        x = random.choice(range(3, 100, 2))  # Generate odd x
        y = random.randint(1, 100)  # y can remain any integer
        return (x, y)
    return individual

# Main Genetic Algorithm function
def genetic_algorithm(population_size=20, generations=10, mutation_rate=0.2):

    # Initialize the population with random (x, y) pairs, ensuring x is odd
    population = [(random.choice(range(3, 100, 2)), random.randint(1, 100)) for _ in range(population_size)]
    
    bests={}

    arr = np.array(target_array)
    target_max=len([item for item in arr.flatten() if isinstance(item, str) and item.isalpha()])
    for generation in range(generations):
        # Evaluate fitness for each individual in the population
        fitness_scores = [fitness(individual) for individual in population]
        
        best_individual = population[fitness_scores.index(max(fitness_scores))]
        bests[max(fitness_scores)]=best_individual
        
        print(f"Best solution in generation {generation}: {max(fitness_scores)} {best_individual}")
        


        # Check if we found a solution (fitness == max)
        if max(fitness_scores) == target_max:            
            print(f"Solution found at generation {generation}: {max(fitness_scores)} {best_individual}")
            return best_individual
        
        # Create a new population by selecting parents and applying crossover and mutation
        new_population = []
        for _ in range(population_size // 2):  # Each iteration generates two offspring
            parent1, parent2 = select_parents(population, fitness_scores,target_max)
            offspring1 = crossover(parent1, parent2)
            offspring2 = crossover(parent2, parent1)
            new_population.append(mutate(offspring1, mutation_rate))
            new_population.append(mutate(offspring2, mutation_rate))
        
        population = new_population  # Replace the old population with the new one

    # If no solution is found, return the best individual
    # Find the maximum key and corresponding value
    max_score = max(bests.keys())
    best_individual = bests[max_score]
    print(f"Best solution after {generations} generations: {max_score} {best_individual}")
    return best_individual


# Load the image in grayscale
img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Run the genetic algorithm
best_values = genetic_algorithm()
print(f"Best x and y values found: {best_values}")

# f=fitness((23,45))
# print(f)