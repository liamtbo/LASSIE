add in marion's new images for Loc2 and 3 for each label

add in a slide showing all curves displayed as points on a pca plot as well as highlighting in red where we are in the approach slide

add in more slides that shows a curve switching labels

update PCA explanation


order:
    feature extractino
    pca
    resulting in cluster

    
Hi everyone thanks for coming.
My presentation today is about an analysis of marions labeling and a pseudo clustering approach
Lets jump right in

our data consists of 133 penetration csv's from ws 23 and 25
Marion has labeled around 37% of these and the remaining are unlabeled
We chose features to represent each curve.
next we converted each penetration curve into a feature representation using these chosen features
After this, for each label category, we calclate the feature mean of every point assigned to this category
Finally, we pseudo label the data by assigning each unlabeled point to the closes label category mean/centroid
Any question's regarding this process?
Let's talk about the data

Our data is from WS23 25.
All the labeled data is from WS23
and here on the left we can see each one of Marion's label category along with it's frequency

Here is the bubbly surface, with images and a plotting of the respective images
...
Here are all the label categories in one slide to compare

Next we'll talk about the features we choose to represent each pen curve

One thing to consider with feature selection is the featuer correlation with one another. Highly correlated features will elongate the data diagnoally in their direction. This can lead to poor clustering results. I choose a threshold of 0.8 as a cutoff

after the processing steps of extracting features from each curve, and finding the feature means of every label category, We do a pseudo labeling