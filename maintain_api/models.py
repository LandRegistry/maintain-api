from maintain_api.extensions import db


class Categories(db.Model):
    __tablename__ = 'charge_categories'

    id = db.Column('id', db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(), nullable=False)
    display_name = db.Column('display_name', db.String(), nullable=False)
    parent_id = db.Column('parent_id', db.Integer(), db.ForeignKey('charge_categories.id'), nullable=True)
    display_order = db.Column('display_order', db.Integer(), nullable=True)
    permission = db.Column('permission', db.String(), nullable=True)
    children = db.relationship("Categories", lazy="joined", order_by="asc(Categories.display_order)", join_depth=2)
    provisions = db.relationship("CategoryStatProvisionMapping", lazy="joined", back_populates="category")
    instruments = db.relationship("CategoryInstrumentsMapping", lazy="joined", back_populates="category")

    def __init__(self, name, parent_id, display_order, permission, display_name):
        self.name = name
        self.parent_id = parent_id
        self.display_order = display_order
        self.permission = permission
        self.display_name = display_name


class Instruments(db.Model):
    __tablename__ = 'instruments'

    id = db.Column('id', db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(), nullable=False)
    categories = db.relationship("CategoryInstrumentsMapping", back_populates="instrument")

    def __init__(self, name):
        self.name = name


class StatutoryProvision(db.Model):
    __tablename__ = 'statutory_provision'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    selectable = db.Column(db.Boolean, nullable=False, server_default='t')
    categories = db.relationship("CategoryStatProvisionMapping", back_populates="provision")

    def __init__(self, title, selectable=True):
        self.title = title
        self.selectable = selectable


class CategoryStatProvisionMapping(db.Model):
    __tablename__ = 'charge_categories_stat_provisions'
    __table_args__ = (db.PrimaryKeyConstraint('category_id', 'statutory_provision_id'),)

    category_id = db.Column('category_id', db.Integer(), db.ForeignKey('charge_categories.id'), nullable=False)
    statutory_provision_id = db.Column('statutory_provision_id', db.Integer(),
                                       db.ForeignKey('statutory_provision.id'), nullable=False)
    category = db.relationship("Categories", back_populates="provisions")
    provision = db.relationship("StatutoryProvision", back_populates="categories")

    def __init__(self, category_id, statutory_provision_id):
        self.category_id = category_id
        self.statutory_provision_id = statutory_provision_id


class CategoryInstrumentsMapping(db.Model):
    __tablename__ = 'charge_categories_instruments'
    __table_args__ = (db.PrimaryKeyConstraint('category_id', 'instruments_id'),)

    category_id = db.Column('category_id', db.Integer(), db.ForeignKey('charge_categories.id'), nullable=False)
    instruments_id = db.Column('instruments_id', db.Integer(), db.ForeignKey('instruments.id'), nullable=False)
    category = db.relationship("Categories", back_populates="instruments")
    instrument = db.relationship("Instruments", back_populates="categories")

    def __init__(self, category_id, instruments_id):
        self.category_id = category_id
        self.instruments_id = instruments_id
