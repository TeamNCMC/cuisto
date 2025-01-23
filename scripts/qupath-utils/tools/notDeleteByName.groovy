/**
 * notDeleteByName.groovy
 *
 * Delete all annotations whose Name DO NOT correspond to the specified one.
 */

// Define what Names to NOT delete
def nameToNotDelete = ["DH", "VH"]

// Find objects to delete
toRemove = getAnnotationObjects().findAll { !nameToNotDelete.contains(it.getName())}

// remove selected objects
removeObjects(toRemove, true)