from typing import Optional
from sqlalchemy import String, Integer, Boolean, Enum as PgEnum, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from anonchat.domain.user.enums import Gender, Locale, UserStatus, UserPromotion
from anonchat.infrastructure.database.models.base import Base


class UserReputationModel(Base):
    __tablename__ = "user_reputation"

    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("users.user_id", ondelete="CASCADE"), 
        primary_key=True
    )
    likes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dislikes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="reputation_relation")


class UserSettingsModel(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("users.user_id", ondelete="CASCADE"), 
        primary_key=True
    )
    search_gender: Mapped[Gender] = mapped_column(
        PgEnum(Gender, name="gender_enum"), 
        nullable=False, 
        default=Gender.ANY
    )
    min_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    user: Mapped["UserModel"] = relationship(back_populates="settings_relation")


class UserInterestModel(Base):
    __tablename__ = "user_interests"

    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("users.user_id", ondelete="CASCADE"), 
        primary_key=True
    )
    interest_id: Mapped[int] = mapped_column(Integer, primary_key=True)


class UserModel(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    gender: Mapped[Gender] = mapped_column(PgEnum(Gender, name="gender_enum"), nullable=False)
    locale: Mapped[Locale] = mapped_column(PgEnum(Locale, name="locale_enum"), default=Locale.UNSET)

    status_value: Mapped[UserStatus] = mapped_column(
        PgEnum(UserStatus, name="user_status_enum"), 
        default=UserStatus.ACTIVE, 
        nullable=False
    )
    promotion: Mapped[UserPromotion] = mapped_column(
        PgEnum(UserPromotion, name="user_promotion_enum"), 
        default=UserPromotion.USER, 
        nullable=False
    )
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    settings_relation: Mapped["UserSettingsModel"] = relationship(
        "UserSettingsModel",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="joined",
        back_populates="user"
    )

    reputation_relation: Mapped["UserReputationModel"] = relationship(
        "UserReputationModel",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="joined",
        back_populates="user"
    )

    interests_relation: Mapped[list["UserInterestModel"]] = relationship(
        "UserInterestModel",
        uselist=True,
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.user_id}, username={self.username})>"
