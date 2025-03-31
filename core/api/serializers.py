from rest_framework import serializers
from core.models import InternalUser, InternalUserSkillset, JobOffer, Company, JobApplication, CoreSkill, \
    SecondarySkill


class InternalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalUser
        fields = '__all__'


class JobOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'


class InternalUserSkillsetSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalUserSkillset
        fields = '__all__'


class CoreSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreSkill
        fields = '__all__'


class SecondarySkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondarySkill
        fields = '__all__'


class AuthInputSerializer(serializers.Serializer):
    provider = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    code_verifier = serializers.CharField(required=False)

class AuthUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    name = serializers.CharField()

class AuthResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    user = AuthUserSerializer()
