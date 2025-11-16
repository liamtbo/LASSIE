

Problem
As the ability to conduct robotic off-planet data collection grows, so does the need for label creation and an efficient data labeling processes. 

Solution
To create the classification bins, we propose a framework involving a planetary soil expert and unsupervised clustering algorithms. Once these categorical bins have been created, we utilize machine learning pseudo labeling techniques to accurately and efficiently predict labels for the unlabeled data.

Impact









Long-term goal: quadruped walks on a terrain and uses force-depth data to classify each step into categorical bins

Current goal: create those classification bins for white sands data

assumption: since we want to use quadruped steps to classify the terrain, we assume each class has a unique type of force depth plot
    i.e. one class has crust breaks, a different class has very high force values, ect.

how do we create these classifications?

unsupervised clustering is good at classifying data such that each class has a unique force-depth plots, exactly what our objective is.

If Marion's goal for her surface classification is that each class has a unique force-depth plot type, then I propose a solution to her visual feature choice problem.

    proposed solution:
        use unsupervised clustering models (Kmeans, dbscan, ect) to cluster the force depth curve data
        for each cluster (classification):
            collect all the photos corresponding to this cluster
            look for common visual features within these photos
            use these common visual features to represent that class

Is our objective 