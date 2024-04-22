swde_prompt = {
    'meta': 'It\'s worth noticing that the candidate attribute values are the non-empty strings contained in text nodes in the corresponding DOM tree, and one page may contain multiple distinct values that correspond to an attribute.',
    'auto': {
        'meta': 'Here\'s a webpage with detail information of an auto.',
        'model': 'Please extract the model of the auto.', 
        'price': 'Please extract the price of the auto.', 
        'engine': 'Please extract the engine of the auto.', 
        'fuel_economy': 'Please extract the fuel efficiency of the auto.'
    },
    'book': {
        'meta': 'Here\'s a webpage with detail information of a book.',
        'title': 'Please extract the title of the book.', 
        'author': 'Please extract the author of the book.', 
        'isbn_13': 'Please extract the isbn number of the book.', 
        'publisher': 'Please extract the publisher of the book.', 
        'publication_date': 'Please extract the publication date of the book.'
    },
    'camera': {
        'meta': 'Here\'s a webpage with detail information of camera.',
        'model': 'Please extract the product name of the camera.', 
        'price': 'Please extract the sale price of the camera.', 
        'manufacturer': 'Please extract the manufactor of the camera.',
    },
    'job': {
        'meta': 'Here\'s a webpage with detail information of a job.',
        'title': 'Please extract the title of the job.', 
        'company': 'Please extract the name of company that offers the job.', 
        'location': 'Please extract the working location of the job.', 
        'date_posted': 'Please extract the date that post the job.'
    },
    'movie': {
        'meta': 'Here\'s a webpage with detail information of a movie.',
        'title': 'Please extract the title of the movie.',
        'director': 'Please extract the director of the movie.',
        'genre': 'Please extract the genre of the movie.',
        'mpaa_rating': 'Please extract the MPAA rating of the movie.'
    },
    'nbaplayer': {
        'meta': 'Here\'s a webpage with detail information of an NBA player.',
        'name': 'Please extract the name of the player.', 
        'team': 'Please extract the team of the player he play now.', 
        'height': 'Please extract the height of the player.', 
        'weight': 'Please extract the weight of the player.'
    },
    'restaurant': {
        'meta': 'Here\'s a webpage with detail information of a restaurant.',
        'name': 'Please extract the restaurant\'s name.',
        'address': 'Please extract the retaurant\'s address.', 
        'phone': 'Please extract the restaurant\'s phone number.', 
        'cuisine': 'Please extract the cuisine that the restaurant offers.'
    },
    'university': {
        'meta': 'Here\'s a webpage on detail information of a university.',
        'name': 'Please extract the name of the university.', 
        'phone': 'Please extract the contact phone number of the university.', 
        'website': 'Please extract the website url of the university.', 
        'type': 'Please extract the type of the university.',
    }
}