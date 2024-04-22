SCHEMA = {
    #allmovie
    'movie-allmovie(2000)':['AMG Work ID', 'Category', 'Color Type', 'Countries', 'Director', 'Flags', 'Genres', 'Keywords', 'MPAA Rating', 'Moods', 'Other Related Works | Is related to:', 'Plot Synopsis', 'Produced by', 'Run Time', 'Similar Works', 'Themes', 'Tones', 'Types', 'Year', 'topic_entity_name'],
    #amctv
    'movie-amctv(2000)':['Category:', 'Country:', 'Director:', 'Filmed In:', 'Genre/Type:', 'Key Cast:', 'Keywords:', 'Language:', 'MPAA Rating:', 'Produced By:', 'Run Time:', 'Themes:', 'Year:'],
    #hollywood
    'movie-hollywood(2000)':['Full Cast & Crew | Art Department | Production Designer', 'Full Cast & Crew | Cast', 'Full Cast & Crew | Director', 'Full Cast & Crew | Distribution Companies', 'Full Cast & Crew | Film Camera | Cinematographer', 'Full Cast & Crew | Music | Composer (Music Score)', 'Full Cast & Crew | Producers | Producer', 'Full Cast & Crew | Wardrobe Hair Makeup | Costume Designer', 'Full Cast & Crew | Writer | Screenwriter', 'Synopsis', 'Theatrical Release', 'topic_entity_name'],
    #iheartmovies
    'movie-iheartmovies(2000)':['Directed by', 'Genres', 'Language', 'Length', 'MPAA Rating', 'Released', 'Written by', 'topic_entity_name'],
    #imdb
    'movie-imdb(2000)':['Box Office | Budget:', 'Box Office | Gross:', 'Box Office | Opening Weekend:', 'Company Credits | Production Co:', 'Critics:', 'Details | Also Known As:', 'Details | Country:', 'Details | Filming Locations:', 'Details | Language:', 'Details | Release Date:', 'Director:', 'Full cast and crew | Cast overview, first billed only: | Cast', 'Fun Facts | Connections', 'Fun Facts | Goofs', 'Fun Facts | Quotes', 'Fun Facts | Soundtracks', 'Fun Facts | Trivia', 'Genres:', 'MPAA | Motion Picture Rating', 'Message Boards', 'Plot Keywords:', 'Recommendations', 'Related Lists', 'Related News', 'Stars:', 'Storyline', 'Taglines:', 'Technical Specs | Aspect Ratio:', 'Technical Specs | Color', 'Technical Specs | MOVIEmeter:', 'Technical Specs | Runtime:', 'Technical Specs | Sound Mix:', 'Users: (', 'topic_entity_name'],
    #metacritic
    'movie-metacritic(2000)':['Critic Reviews | Mixed: | Mixed&&&Critic Reviews', 'Critic Reviews | Negative: | Negative&&&Critic Reviews', 'Critic Reviews | Positive: | Positive&&&Critic Reviews', 'Director:', 'Genre(s):', 'Metascore', 'Rating:', 'Release Date:', 'Reviewed by:', 'Runtime:', 'Starring:', 'Studio:', 'User Reviews | Mixed: | Mixed&&&User Reviews', 'User Reviews | Negative: | Negative&&&User Reviews', 'User Reviews | Positive: | Positive&&&User Reviews', 'User Score', 'topic_entity_name'],
    #rottentomatoes
    'movie-rottentomatoes(2000)':['Cast', 'Directed By:', 'Distributor:', 'Genre:', 'In Theaters:', 'Rated:', 'Running Time:', 'Synopsis:', 'Written By:', 'topic_entity_name'],
    #yahoo
    'movie-yahoo(2000)':['Cast and Credits | Directed by:', 'Cast and Credits | Produced by:', 'Cast and Credits | Starring:', 'Genres:', 'MPAA Rating:', 'Release Date:', 'Running Time:', 'U.S. Box Office:', 'Yahoo! Users:', 'topic_entity_name'],
    #espn(434)
    'nbaplayer-espn(434)':['Age', 'Birth Date', 'Birth Place', 'Height', 'Next Game:', 'PPG', 'Position', 'Salary', 'Weight', 'topic_entity_name'],
    #fanhouse(446)
    'nbaplayer-fanhouse(446)': ['APG', 'Age', 'Birthplace', 'Born', 'College', 'Experience', 'Height', 'Name', 'PPG', 'Position', 'RPG', 'Team', 'Weight', 'topic_entity_name'],
    #foxsports(425)
    'nbaplayer-foxsports(425)': ['Age', 'Born', 'College', 'Ht', 'INJURY STATUS', 'Impact', 'News', 'Source', 'Wt', 'topic_entity_name'],
    #msnca(434)
    'nbaplayer-msnca(434)':['APG', 'Birthplace:', 'Born:', 'College:', 'Draft:', 'Height:', 'PPG', 'Position:', 'RPG', 'Team:', 'Weight:', 'topic_entity_name'],
    #si(515)
    'nbaplayer-si(515)':['APG', 'Age:', 'Born:', 'College:', 'FG%', 'Height:', 'NBA Experience:', 'PPG', 'RPG', 'Rookie Year:', 'Weight:', 'topic_entity_name'],
    #slam(423)
    'nbaplayer-slam(423)':['Assists/Game (APG)', 'Birthdate', 'Birthplace', 'Blocks (BLK)', 'Games', 'Height', 'Points/Game (PPG)', 'Position', 'Rebounds/Game (RPG)', 'Steals', 'Weight', 'topic_entity_name'],
    #usatoday(436)
    'nbaplayer-usatoday(436)':['Age:', 'DOB:', 'Height:', 'Weight:', 'topic_entity_name'],
    #yahoo(438)
    'nbaplayer-yahoo(438)':['Ast', 'Born', 'College', 'Draft', 'Height', 'Pts', 'Reb', 'Weight', 'topic_entity_name'],
    #collegeprowler(2000)
    'university-collegeprowler(2000)': ['Academic Calendar:', 'Admission Difficulty:', 'Control:', 'FT Undergraduates:', 'Location:', 'Religious Affiliation:', 'School Contact', 'School Contact | *phone', 'School Contact | *street address', 'School Contact | *website', 'Setting:', 'Tuition:', 'Undergrad Student Body | Full-Time:', 'Undergrad Student Body | Total Female:', 'Undergrad Student Body | Total Male:', 'topic_entity_name', 'Cost | Books and Supplies:', 'Undergrad Student Body | Part-Time:'],
    #ecampustours(1063)
    'university-ecampustours(1063)': ['Degree Programs: | Highest degree offered:', 'Degrees Include:', 'Demographics | Affiliation', 'Demographics | Calendar System', 'Demographics | Enrollment*', 'Demographics | Institution', 'Demographics | Private School', 'Demographics | Student Body', 'Demographics | Tuition*', 'Demographics | Year Established', 'School Details | *city/state/zip', 'School Details | *website', 'School Details | Phone:', 'topic_entity_name'],
    #embark(2000)
    'university-embark(2000)': ['Application Information| Early Action Deadline:', 'Application Information| Early Decision Deadline:', 'Application Information| Priority Application Deadline:', 'Application Information| Regular Application Deadline:', 'Cost and Financial Aid| Average Total Freshmen Need-based Aid:', 'Cost and Financial Aid| Direct Lender:', 'Cost and Financial Aid| In-State Tuition:', 'Cost and Financial Aid| Out-of-State Tuition:', 'Cost and Financial Aid| Undergrads Receiving Need-based Financial Aid:', 'Phone:', 'Programs| ', 'Statistics| ACT Composite Middle 50%:', 'Statistics| Average High School GPA:', 'Statistics| Average Math SAT:', 'Statistics| Average Verbal SAT:', 'Statistics| Degree Type:', 'Statistics| Enrollment:', 'Statistics| Most Popular Majors:', 'Statistics| School Type:', 'Statistics| Setting:', 'Statistics| Student Faculty Ratio:', 'topic_entity_name', 'Fax:'],
    #matchcollege(2000)
    'university-matchcollege(2000)':['Calendar System:', 'Facilities and Programs Offered', 'General Phone:', 'Highest Degree:', 'Local Area:', 'OPEID College Code:', 'Overall Student Enrollment | Total Student Enrollment:', 'Source:', 'Student Attendance | Total Student Attendance | Full-Time: | Total Student Attendance&&&Full-Time:', 'Student Attendance | Total Student Attendance | Part-Time: | Total Student Attendance&&&Part-Time:', 'Student Gender | Total Student Gender | Female: | Total Student Gender&&&Female:', 'Student Gender | Total Student Gender | Male: | Total Student Gender&&&Male:', 'Type:', 'Website', 'topic_entity_name'],
    #usnews(1027)
    'university-usnews(1027)':['Admissions E-mail:', 'College Category', 'Overview | General Information | 2009 Endowment:', 'Overview | General Information | Academic calendar:', 'Overview | General Information | Fall Admissions | Application deadline', 'Overview | General Information | Fall Admissions | Application fee', 'Overview | General Information | Fall Admissions | Fall 2009 acceptance rate', 'Overview | General Information | Fall Admissions | Selectivity', 'Overview | General Information | Institutional Control:', 'Overview | General Information | Mission (as provided by the school)', 'Overview | General Information | Religious affiliation:', 'Overview | General Information | Setting:', 'Overview | General Information | Total undergraduate enrollment', 'Overview | General Information | Year founded:', 'Rank', 'Score', 'Tier', 'Web site:', 'topic_entity_name'],
}