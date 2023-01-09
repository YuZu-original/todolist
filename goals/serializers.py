from django.db import transaction
from rest_framework import serializers

from core.models import User
from core.serializers import UserSerializer
from goals.models import Board
from goals.models import BoardParticipant
from goals.models import Goal
from goals.models import GoalCategory
from goals.models import GoalComment


# BoardParticipant


class BoardParticipantSerializer(serializers.ModelSerializer):
    """Serializer for `BoardParticipant`"""

    role = serializers.ChoiceField(
        required=True, choices=BoardParticipant.editable_choices
    )
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = BoardParticipant
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "board")


# Board


class BoardCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating `Board`"""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        read_only_fields = ("id", "created", "updated")
        fields = "__all__"

    def create(self, validated_data):
        user = validated_data.pop("user", self.context["request"].user)
        board = Board.objects.create(**validated_data)
        BoardParticipant.objects.create(
            user=user, board=board, role=BoardParticipant.Role.owner
        )
        return board


class BoardSerializer(serializers.ModelSerializer):
    """Serializer for `Board`"""

    participants = BoardParticipantSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = "__all__"
        read_only_fields = ("id", "created", "updated")

    def update(self, instance, validated_data):
        owner = validated_data.pop("user", self.context["request"].user)

        with transaction.atomic():
            if validated_data.get("participants"):
                new_participants = validated_data.pop("participants")
                new_by_id = {
                    part["user"].id: part for part in new_participants
                }

                old_participants = instance.participants.exclude(user=owner)

                for old_participant in old_participants:
                    if old_participant.user_id not in new_by_id:
                        old_participant.delete()
                        continue
                    if (
                        old_participant.role
                        != new_by_id[old_participant.user_id]["role"]
                    ):
                        old_participant.role = new_by_id[
                            old_participant.user_id
                        ]["role"]
                        old_participant.save()
                    new_by_id.pop(old_participant.user_id)
                for new_part in new_by_id.values():
                    BoardParticipant.objects.create(
                        board=instance,
                        user=new_part["user"],
                        role=new_part["role"],
                    )
            if validated_data.get("title"):
                instance.title = validated_data.get("title")
            instance.save()

        return instance


class BoardListSerializer(serializers.ModelSerializer):
    """Serializer for list of `Board`"""

    class Meta:
        model = Board
        fields = "__all__"


# GoalCategory


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating `GoalCategory`"""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_board(self, value):
        if value.is_deleted:
            raise serializers.ValidationError("not allowed in deleted board")
        if not BoardParticipant.objects.filter(
            board=value,
            role__in=[
                BoardParticipant.Role.owner,
                BoardParticipant.Role.writer,
            ],
            user=self.context["request"].user,
        ).exists():
            raise serializers.ValidationError(
                "you do not have permission to create goal category in this board"
            )
        return value


class GoalCategorySerializer(serializers.ModelSerializer):
    """Serializer for `GoalCategory`"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "board")


# Goal


class GoalCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating `Goal`"""

    category = serializers.PrimaryKeyRelatedField(
        queryset=GoalCategory.objects.all()
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_category(self, value):
        if value.is_deleted:
            raise serializers.ValidationError(
                "not allowed in deleted category"
            )

        if not BoardParticipant.objects.filter(
            board_id=value.board_id,
            role__in=[
                BoardParticipant.Role.owner,
                BoardParticipant.Role.writer,
            ],
            user=self.context["request"].user,
        ).exists():
            raise serializers.ValidationError(
                "you do not have permission to create goal in this board"
            )
        return value


class GoalSerializer(serializers.ModelSerializer):
    """Serializer for `Goal`"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_category(self, value):
        if value.is_deleted:
            raise serializers.ValidationError(
                "not allowed in deleted category"
            )

        if self.instance.category.board_id != value.board_id:
            raise serializers.ValidationError(
                "this category does not belong to this board"
            )
        return value


# Comment


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating `GoalComment`"""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")

    def validate_goal(self, value):
        if not BoardParticipant.objects.filter(
            board_id=value.category.board_id,
            role__in=[
                BoardParticipant.Role.owner,
                BoardParticipant.Role.writer,
            ],
            user=self.context["request"].user,
        ).exists():
            raise serializers.ValidationError(
                "you do not have permission to create comment in this board"
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for `GoalComment`"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "goal")
