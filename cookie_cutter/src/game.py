import random

import comms
from object_types import ObjectTypes


class Game:
    """
    Stores all information about the game and manages the communication cycle.
    Available attributes after initialization will be:
    - tank_id: your tank id
    - objects: a dict of all objects on the map like {object-id: object-dict}.
    - width: the width of the map as a floating point number.
    - height: the height of the map as a floating point number.
    - current_turn_message: a copy of the message received this turn. It will be updated everytime `read_next_turn_data`
        is called and will be available to be used in `respond_to_turn` if needed.
    """
    def __init__(self):
        tank_id_message: dict = comms.read_message()
        self.tank_id = tank_id_message["message"]["your-tank-id"]
        self.enemy_tank_id = tank_id_message["message"]["enemy-tank-id"]

        self.current_turn_message = None

        # We will store all game objects here
        self.objects = {}

        next_init_message = comms.read_message()
        while next_init_message != comms.END_INIT_SIGNAL:
            # At this stage, there won't be any "events" in the message. So we only care about the object_info.
            object_info: dict = next_init_message["message"]["updated_objects"]

            # Store them in the objects dict
            self.objects.update(object_info)

            # Read the next message
            next_init_message = comms.read_message()

        # We are outside the loop, which means we must've received the END_INIT signal

        # Let's figure out the map size based on the given boundaries

        # Read all the objects and find the boundary objects
        boundaries = []
        for game_object in self.objects.values():
            if game_object["type"] == ObjectTypes.BOUNDARY.value:
                boundaries.append(game_object)

        # The biggest X and the biggest Y among all Xs and Ys of boundaries must be the top right corner of the map.

        # Let's find them. This might seem complicated, but you will learn about its details in the tech workshop.
        biggest_x, biggest_y = [
            max([max(map(lambda single_position: single_position[i], boundary["position"])) for boundary in boundaries])
            for i in range(2)
        ]

        self.width = biggest_x
        self.height = biggest_y

    def read_next_turn_data(self):
        """
        It's our turn! Read what the game has sent us and update the game info.
        :returns True if the game continues, False if the end game signal is received and the bot should be terminated
        """
        # Read and save the message
        self.current_turn_message = comms.read_message()

        # Break out condition
        if self.current_turn_message == comms.END_SIGNAL:
            return False

        # Delete the objects that have been deleted
        # NOTE: You might want to do some additional logic here. For example check if a powerup you were moving towards
        # is already deleted, etc.
        for deleted_object_id in self.current_turn_message["message"]["deleted_objects"]:
            try:
                del self.objects[deleted_object_id]
            except KeyError:
                pass

        # Update your records of the new and updated objects in the game
        # NOTE: you might want to do some additional logic here. For example check if a new bullet has been shot or a
        # new powerup is now spawned, etc.
        self.objects.update(self.current_turn_message["message"]["updated_objects"])

        return True

    def respond_to_turn(self):
        """
        This is where you should write your bot code to process the data and respond to the game.
        """

        # Write your code here... For demonstration, this bot just shoots randomly every turn.
         # Example implementation:
        
        all_object_ids = self.objects.keys()
        
        print(all_object_ids)
        
        # Get the current position of your tank
        my_tank = self.objects.get(self.tank_id)
        if my_tank is None:
            return

        # Decide on a random movement direction (for demonstration purposes)
        move_direction = random.randint(0, 360)

        # Shoot at a random angle (for demonstration purposes)
        shoot_angle = random.uniform(0, 360)

        # Post the movement and shooting actions
        comms.post_message({"move": move_direction})
        comms.post_message({"shoot": shoot_angle})
        

    def check_wall(self):
        '''
        Checks if we hit a boundary, wall, or tank

        "destructibleWall-id": {
            "type": 4,
            "position": [356.12, 534.39],
            "hp": 1
        }

        "boundary-id": {
            "type": 6, 
            "position": [
                [1.50, 998.5],
                [1.50, 1.50],
                [1798.5, 1.50],
                [1798.5, 998.5]
            ], 
            "velocity": [
                [10.0, 0.0],
                [0.0, 10.0],
                [-10.0, 0.0],
                [0.0, -10.0]
            ]
        }

        "wall-id": {
            "type": 3,
            "position": [356.12, 534.39]
        }
        '''
        # WALL
        # check if our position is near another position
        

        pass


    
import math
## HELPER FUNCTIONS 
def distance(point1, point2):

    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

def calculate_projected_position(position, velocity, time):
    x = position[0] + velocity[0] * time
    y = position[1] + velocity[1] * time
    return [x, y]

def prioritize_bullets(self, tank):
    '''
    Class function
    Returns list of bullets based on their closeness to hitting the current tank 
            (based on tank and bullet trajectory)
    '''
    tank_position = tank["position"]
    tank_velocity = tank["velocity"]
    bullet_priority = []

    for bullet in self.objects.values():
        if bullet == ObjectTypes.BULLET:
 
            bullet_position = bullet["position"]
            bullet_velocity = bullet["velocity"]

            # Calculate the time of intersection between the bullet and the tank
            time_x = (tank_position[0] - bullet_position[0]) / (bullet_velocity[0] - tank_velocity[0])
            time_y = (tank_position[1] - bullet_position[1]) / (bullet_velocity[1] - tank_velocity[1])
            time = max(time_x, time_y)

            # Calculate the projected position of the tank and bullet at the time of intersection
            tank_projected_position = calculate_projected_position(tank_position, tank_velocity, time)
            bullet_projected_position = calculate_projected_position(bullet_position, bullet_velocity, time)

            # Calculate the distance between the tank and the bullet's projected position
            distance_to_bullet = distance(tank_projected_position, bullet_projected_position)

            bullet_priority.append((bullet, distance_to_bullet))

    # Sort bullets by distance in ascending order (closer bullets have higher priority)
    bullet_priority.sort(key=lambda x: x[1])

    # Return a sequence of bullets in order of priority
    return [bullet_id for bullet_id, _ in bullet_priority]





