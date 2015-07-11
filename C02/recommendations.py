# -*- coding=utf-8 -*-
from math import sqrt
# A dictionary of movie critics and their ratings of a small set of movies
critics = {
    'Lisa Rose': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'Superman Returns': 3.5,
        'You, Me and Dupree': 2.5,
        'The Night Listener': 3.0,
    },
    'Gene Seymour': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 1.5,
        'Superman Returns': 5.0,
        'The Night Listener': 3.0,
        'You, Me and Dupree': 3.5,
    },
    'Michael Phillips': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.0,
        'Superman Returns': 3.5,
        'The Night Listener': 4.0,
    },
    'Claudia Puig': {
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'The Night Listener': 4.5,
        'Superman Returns': 4.0,
        'You, Me and Dupree': 2.5,
    },
    'Mick LaSalle': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'Just My Luck': 2.0,
        'Superman Returns': 3.0,
        'The Night Listener': 3.0,
        'You, Me and Dupree': 2.0,
    },
    'Jack Matthews': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'The Night Listener': 3.0,
        'Superman Returns': 5.0,
        'You, Me and Dupree': 3.5,
    },
    'Toby': {
        'Snakes on a Plane': 4.5, 
        'You, Me and Dupree': 1.0,
        'Superman Returns': 4.0
    },
}

def sim_distance(prefs, p1, p2):
    ''' Returns a distance-based similarity score for person1 and person2. '''
    si = set(prefs[p1]) & set(prefs[p2])
    # If they are no ratings in common, return 0
    if len(si) == 0:
        return 0

    sum_of_squares = sum([pow(prefs[p1][item] - prefs[p2][item], 2) for item in prefs[p1] if item in prefs[p2]])

    return 1/(1+sqrt(sum_of_squares))
        

def sim_pearson(prefs, p1, p2):
    ''' Returns the Pearson correlation coefficient for person1 and person2. '''
    si = set(prefs[p1]) & set(prefs[p2])
    n = len(si)
    # If they are no ratings in common, return 1 
    if n==0: return 1

    # Sums of all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # Sums of the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si]) 
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si]) 
    
    # Sum of the products
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])
    
    # Calculate Pearson score
    num = pSum - (sum1*sum2/n)
    den = sqrt((sum1Sq - pow(sum1, 2)/n) * (sum2Sq - pow(sum2, 2)/n))
    if den == 0:
        return 0

    return num/den

def topMatches(prefs, person, n=5, similarity=sim_pearson):
    ''' 
    Returns the best matches for person from the prefs dictionary. 
    Number of results and similarity function are optional params.
    '''
    scores = [(similarity(prefs, person, other), other) for other in prefs if other!=person]
    scores.sort()
    scores.reverse()
    return scores[0:n]


def getRecommendations(prefs, person, similarity=sim_pearson):
    '''
    Gets recommendations for a person by using a weighted average
    of every other user's rankings
    '''
    totals = {}
    simSums = {}
    for other in prefs:
        if other == person: 
            continue
        sim = similarity(prefs, person, other)
        if sim<=0:
            continue
        for item in prefs[other]:
            # Only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item]*sim
                simSums.setdefault(item, 0)
                simSums[item] += sim
    rankings = [(total/simSums[item], item) for item, total in totals.items()]

    rankings.sort()
    rankings.reverse()
    return rankings
            

def transformPrefs(prefs):
    '''
    Transform the recommendations into a mapping where persons are described
    with interest scores for a given title e.g. {title: person} instead of
    {person: title}.
    '''
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            result[item][person] = prefs[person][item]
    return result


def calculateSimilarItems(prefs, n=10):
    '''
    Create a dictionary of items showing which other items they are
    most similar to.
    '''
    result = {}
    # Invert the preference matrix to be item-centric
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        c += 1
        if c % 100 == 0: print "%d / %d" % (c, len(itemPrefs))
        # Find the most similar items to this one
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result

def getRecommendedItems(prefs, itemMatch, user):
    ''' Get recommended items using item-based collaborative filtering '''
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    # Loop over items rated by this user 
    for (item, rating) in userRatings.items():
        # Loop over items similar to this one
        for (similarity, item2) in itemMatch[item]:
            if item2 in userRatings: continue
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity
            
    rankings = [(score/totalSim[item], item) for item, score in scores.items()]
        
    rankings.sort()
    rankings.reverse()
    return rankings


def LoadMovieLens(path='ml-1m'):
#def LoadMovieLens(path='ml-100k'):
    movies = {}
    with open(path+'/movies.dat', 'r') as m:
    #with open(path+'/u.item', 'r') as m:
        lines = m.readlines()
        for line in lines:
            (id, title) = line.split('::')[0:2]
            #(id, title) = line.split('|')[0:2]
            movies[id] = title

    prefs = {}
    with open(path+'/ratings.dat') as r:
    #with open(path+'/u.data') as r:
        lines = r.readlines()
        for line in lines:
            (userid, movieid, rating, timstamp) = line.split('::')
            #(userid, movieid, rating, timstamp) = line.split('\t')
            prefs.setdefault(userid, {})
            prefs[userid][movies.get(movieid)] = float(rating)

    return prefs
        
    
if __name__=='__main__':
    print "Sumilarity between 'Lisa Rose' and 'Gene Seymour':"
    print "\tsim_distance:", sim_distance(critics, 'Lisa Rose', 'Gene Seymour')
    print "\tsim_pearson:", sim_pearson(critics, 'Lisa Rose', 'Gene Seymour')

    print "topMatches 3 person for Toby:"
    rst = topMatches(critics, 'Toby', n=3) 
    for score, person in rst:
        print '\t', person, ':', score 
    
    print "Get recommendations for Toby(sim_pearson):"
    rst = getRecommendations(critics, 'Toby')
    for score, movie in rst:
        print '\t', movie, ':', score

    print 'Get recommendations for Toby(sim_disctance):'
    rst = getRecommendations(critics, 'Toby', similarity=sim_distance)
    for score, movie in rst:
        print '\t', movie, ':', score

    print "topMatches 3 movies like 'Superman Returns':"
    rst = topMatches(transformPrefs(critics), 'Superman Returns', n=3) 
    for score, movie in rst:
        print '\t', movie, ':', score
        
    print "Get recommendations with 'Just My Luck':"
    rst = getRecommendations(transformPrefs(critics), 'Just My Luck')
    for score, person in rst:
        print '\t', person, ':', score

    print "Calculate Similar Items:"
    itemsim = calculateSimilarItems(critics)
    for movie in itemsim:
        print '\t', movie
        for score, sim_movie in itemsim.get(movie):
            print '\t\t', sim_movie, ':', score

    print "Get recommendations for Toby(item-based):"
    rst = getRecommendedItems(critics, itemsim, 'Toby')
    for score, movie in rst:
        print '\t', movie, ':', score

    print "Get 1M movie data"
    prefs = LoadMovieLens()
    
    print "Calculate similar items(It takes time..)"
    itemsim = calculateSimilarItems(prefs, n=50)
    print "Recommendations for User(id:88):"
    rst = getRecommendedItems(prefs, itemsim, '88')[0:30]
    for score, movie in rst:
        print '\t', movie, ':', score
    
