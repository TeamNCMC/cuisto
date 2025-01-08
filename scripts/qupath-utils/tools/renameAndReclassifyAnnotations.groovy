/**
 * renameAndReclassifyAnnotations.groovy
 *
 * Set the name and classification of existing annotations based
 * on their actual name and classification.
 * Assumes the classification AND name is in the form "Name Hemisphere",
 * and does not contain blank spaces other than the one separating
 * the region name and the hemisphere.
 * Hemispheres can be renamed.
 * Note that this processes all existing annotations, so proceed with
 * caution.
 */

// Parameters
// Hesmishere names : [existing: new]
def hemispheresMap = ["Ipsi": "Left", "Contra": "Right"]

// Get all annotations objects
def annotations = getAnnotationObjects()

// Set classification based on the name
for (annotation in annotations) {
    // split name on blank space
    oldNameParts = annotation.getName().split()
    // get region name which is the first part
    regionName = oldNameParts[0]
    // get hemisphere name which is the second part
    // and convert it to the new name
    hemisphereName = hemispheresMap[oldNameParts[1]]
    // build the new name as hemisphere: region
    newClassification = hemisphereName + ": " + regionName
    // set the new classification
    annotation.setPathClass(getPathClass(newClassification))
    // set the name to the region name only
    annotation.setName(regionName)
}