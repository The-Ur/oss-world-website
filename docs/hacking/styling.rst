Django Best Practice
====================

- Completely avoid Django signals. It just becomes a nightmare for unit-testing.
  Prefer simply using the ``Model.objects.update()`` method.
- Avoid ``null=True`` in ``models.CharField``. Use ``blank=True`` instead.
