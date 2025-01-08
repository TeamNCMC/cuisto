/**
 * setNameAsClassification.groovy
 *
 * Set all annotations' names to their derived classification.
 * Useful to rename the annotations with the region name in the
 * case where the classification is in the form "Left: Region name".
 */

getAnnotationObjects().findAll {
    it.setName(it.getClassifications()[-1])}
