from sqladmin import Admin, ModelView

from app.models.user import User

from app.admin.views.venue import LocationAdmin, VenueAdmin, VenueCategoryAdmin, VenueImageAdmin, VenueSlotAdmin





class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.email,
        User.full_name,
    ]


def setup_admin(app, engine):
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(LocationAdmin)
    admin.add_view(VenueCategoryAdmin)
    admin.add_view(VenueAdmin)
    admin.add_view(VenueImageAdmin)
    admin.add_view(VenueSlotAdmin)
    return admin
