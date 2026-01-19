# yocal

Automated creation of the Orthodox Christian lectionary according to the practice of the Antiochian Archdiocese of the Great Britain and Ireland

## Design decisions

For developers: a place to record why things were done is a particular way.

### `troparia.csv`

This is used to match hymn texts to particular feasts. For major feasts, the `Title` column should be used, and this must match the entry in `menaion.csv`. However, some troparia are to saints who are only mentioned in the list of commemorations, and for these the `Date` column should be used instead.