from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BikeInsurancePolicy(BaseModel):
    name: str
    email: str
    insurer: str
    policy_number: str
    policy_start_date: str
    policy_end_date: str
    date_of_policy: str
    expiry_date: str
    vehicle_type: str

# Vehicle Insurance Models
class VehicleInsuranceFields(BaseModel):
    insuranceCompany: str = Field(default="", description="Insurance company name")
    category: str = Field(description="Vehicle category (bike/car/scooter)")
    product: str = Field(default="Motor", description="Product type")
    policyno: str = Field(default="", description="Policy number")
    lastName: str = Field(default="", description="Customer last name")
    firstName: str = Field(default="", description="Customer first name")
    dob: Optional[str] = Field(default=None, description="Date of birth")
    emailId: str = Field(default="", description="Email address")
    phoneNo: str = Field(default="", description="Phone number")
    lane1: str = Field(default="", description="Address line 1")
    lane2: str = Field(default="", description="Address line 2")
    area: str = Field(default="", description="Area")
    state: str = Field(default="Tamil Nadu", description="State")
    pincode: str = Field(default="", description="Pincode")
    adharNo: Optional[str] = Field(default=None, description="Aadhar number")
    panNo: Optional[str] = Field(default=None, description="PAN number")
    remarks: Optional[str] = Field(default=None, description="Remarks")
    subProduct: str = Field(description="Sub product type")
    policyissuedDate: Optional[str] = Field(default=None, description="Policy issued date")
    commenceMentDate: str = Field(default="", description="Commencement date")
    policyEndDate: str = Field(default="", description="Policy end date")
    sumInsuredIdv: str = Field(default="", description="Sum insured IDV")
    grossPremium: Optional[str] = Field(default=None, description="Gross premium")
    gstPercentage: str = Field(default="", description="GST percentage")

class CovertonImpKeys(BaseModel):
    Coverton_imp_keys: VehicleInsuranceFields

# Medical Insurance Models
class GrossPremiumAndStampDuty(BaseModel):
    gross_premium: str = Field(default="", description="Gross premium amount")
    stamp_duty: str = Field(default="", description="Stamp duty amount")

class RiskDetails(BaseModel):
    emp_dependant_name: str = Field(default="", description="Employee/Dependant name")
    si_no: str = Field(default="", description="SI number")
    no_of_dependants: str = Field(default="", description="Number of dependants")

class InstallmentDetails(BaseModel):
    inst_no: str = Field(default="", description="Installment number")
    installment_percentage: str = Field(default="", description="Installment percentage")
    amount: str = Field(default="", description="Amount")
    tax: str = Field(default="", description="Tax amount")
    total: str = Field(default="", description="Total amount")
    remarks: str = Field(default="", description="Remarks")

class EndorsementScheduleDetails(BaseModel):
    endorsement_no: str = Field(default="", description="Endorsement number")
    endorsement_date: str = Field(default="", description="Endorsement date")

class AgentBrokerDetails(BaseModel):
    agent_broker: str = Field(default="", description="Agent/Broker name")
    address: str = Field(default="", description="Agent/Broker address")

class SalesChannelDetails(BaseModel):
    sales_channel_code: str = Field(default="", description="Sales channel code")
    name: str = Field(default="", description="Sales channel name")

class GenericInformation(BaseModel):
    company_name: str = Field(default="", description="Company name")
    insured_name: str = Field(default="", description="Insured name")
    insured_address: str = Field(default="", description="Insured address")
    plan_type: str = Field(default="", description="Plan type")
    endorsement_schedule: str = Field(default="", description="Endorsement schedule")

class IndividualMemberDetails(BaseModel):
    sl_no: str = Field(default="", description="Serial number")
    name: str = Field(default="", description="Member name")
    dob_and_age: str = Field(default="", description="Date of birth and age")
    relation: str = Field(default="", description="Relation")
    occupation: str = Field(default="", description="Occupation")
    gender: str = Field(default="", description="Gender")
    basic_cover_sum_insured: str = Field(default="", description="Basic cover sum insured")
    cumulative_bonus: str = Field(default="", description="Cumulative bonus")

class NomineeDetails(BaseModel):
    name: str = Field(default="", description="Nominee name")
    relationship_with_insured: str = Field(default="", description="Relationship with insured")

class OptionalCopaymentDetails(BaseModel):
    co_payment_percentage: str = Field(default="", description="Co-payment percentage")

class AmountDetails(BaseModel):
    premium: str = Field(default="", description="Premium amount")
    total_premium: str = Field(default="", description="Total premium")
    cgst: str = Field(default="", description="CGST amount")
    sgst_utgst: str = Field(default="", description="SGST/UTGST amount")
    igst: str = Field(default="", description="IGST amount")
    gst_tds: str = Field(default="", description="GST TDS amount")
    recoverable_stamp_duty: str = Field(default="", description="Recoverable stamp duty")
    total_amount: str = Field(default="", description="Total amount")

class InsurerDetails(BaseModel):
    insured: str = Field(default="", description="Insured name")
    issue_office_name: str = Field(default="", description="Issue office name")
    address: str = Field(default="", description="Office address")
    tel_fax_email: str = Field(default="", description="Telephone/Fax/Email")
    gstin: str = Field(default="", description="GSTIN")
    agent_no: str = Field(default="", description="Agent number")

class PolicyDetails(BaseModel):
    policy_name_schedule: str = Field(default="", description="Policy name/schedule")
    policy_no: str = Field(default="", description="Policy number")
    previous_policy_no: str = Field(default="", description="Previous policy number")
    period_of_insurance: str = Field(default="", description="Period of insurance")
    date_of_insurance: str = Field(default="", description="Date of insurance")
    start_date: str = Field(default="", description="Start date")
    end_date: str = Field(default="", description="End date")
    unique_invoice_no: str = Field(default="", description="Unique invoice number")

class MemberDetails(BaseModel):
    total_members_covered: str = Field(default="", description="Total members covered")
    total_self_covered: str = Field(default="", description="Total self covered")
    total_dependent_covered: str = Field(default="", description="Total dependent covered")

class CoInsuranceDetails(BaseModel):
    insurance_company: str = Field(default="", description="Insurance company")
    share_percentage: str = Field(default="", description="Share percentage")

class PremiumDetails(BaseModel):
    net_premium: str = Field(default="", description="Net premium")
    gross_premium: str = Field(default="", description="Gross premium")

class GstDetails(BaseModel):
    cgst: str = Field(default="", description="CGST amount")
    sgst: str = Field(default="", description="SGST amount")
    ugst: str = Field(default="", description="UGST amount")
    igst: str = Field(default="", description="IGST amount")

class TpaDetails(BaseModel):
    tpa_id: str = Field(default="", description="TPA ID")
    tpa_name: str = Field(default="", description="TPA name")
    tpa_address: str = Field(default="", description="TPA address")
    telephone_no: str = Field(default="", description="Telephone number")
    entity: str = Field(default="", description="Entity")
    email: str = Field(default="", description="Email")

class PolicyConditionsExtensionsEndorsements(BaseModel):
    condition_name: str = Field(default="", description="Condition name")
    description: str = Field(default="", description="Description")
    coverage_amount: str = Field(default="", description="Coverage amount")
    terms: str = Field(default="", description="Terms")

class ThirdPartyDetails(BaseModel):
    third_party_administrator: str = Field(default="", description="Third party administrator")

class IntermediaryAgentDetails(BaseModel):
    name: str = Field(default="", description="Agent name")
    contact_no: str = Field(default="", description="Contact number")
    email: str = Field(default="", description="Email")
    health_id_cards: str = Field(default="", description="Health ID cards")
    industry_type: str = Field(default="", description="Industry type")

class IntermediaryDetails(BaseModel):
    intermediary_name: str = Field(default="", description="Intermediary name")
    code: str = Field(default="", description="Code")
    contact_number: str = Field(default="", description="Contact number")

class OtherInsuredPersonDetails(BaseModel):
    name: str = Field(default="", description="Person name")
    dob: str = Field(default="", description="Date of birth")
    base_sum_insured: str = Field(default="", description="Base sum insured")
    aggregate_deductible: str = Field(default="", description="Aggregate deductible")
    unlimited_restored_addon: str = Field(default="", description="Unlimited restored addon")

class PremiumDetailsAll(BaseModel):
    member_name: str = Field(default="", description="Member name")
    relation: str = Field(default="", description="Relation")
    age: str = Field(default="", description="Age")
    sum_insured: str = Field(default="", description="Sum insured")
    premium_amount: str = Field(default="", description="Premium amount")
    gst_amount: str = Field(default="", description="GST amount")
    total_amount: str = Field(default="", description="Total amount")

class InsuredPersonPremiumDetails(BaseModel):
    name: str = Field(default="", description="Person name")
    relation: str = Field(default="", description="Relation")
    gender: str = Field(default="", description="Gender")
    dob: str = Field(default="", description="Date of birth")
    premium: str = Field(default="", description="Premium")
    gst: str = Field(default="", description="GST")
    total_with_gst: str = Field(default="", description="Total with GST")
    abha_id: str = Field(default="", description="ABHA ID")

class ScheduleOfBenefits(BaseModel):
    benefit_name: str = Field(default="", description="Benefit name")
    description: str = Field(default="", description="Description")
    coverage_amount: str = Field(default="", description="Coverage amount")
    terms_conditions: str = Field(default="", description="Terms and conditions")
    exclusions: str = Field(default="", description="Exclusions")

class PolicyHolderPolicyDetails(BaseModel):
    policy_holder_name: str = Field(default="", description="Policy holder name")
    policy_number: str = Field(default="", description="Policy number")
    start_date: str = Field(default="", description="Start date")
    end_date: str = Field(default="", description="End date")
    premium_amount: str = Field(default="", description="Premium amount")
    coverage_details: str = Field(default="", description="Coverage details")

class MedicalInsurance(BaseModel):
    gross_premium_and_stamp_duty: GrossPremiumAndStampDuty
    risk_details: RiskDetails
    installment_details: InstallmentDetails
    endorsement_schedule_details: EndorsementScheduleDetails
    agent_broker_details: AgentBrokerDetails
    sales_channel_details: SalesChannelDetails
    generic_information: GenericInformation
    individual_member_details: IndividualMemberDetails
    nominee_details: NomineeDetails
    optional_copayment_details: OptionalCopaymentDetails
    amount_details: AmountDetails
    insurer_details: InsurerDetails
    policy_details: PolicyDetails
    member_details: MemberDetails
    co_insurance_details: CoInsuranceDetails
    premium_details: PremiumDetails
    gst_details: GstDetails
    tpa_details: TpaDetails
    policy_conditions_extensions_endorsements: PolicyConditionsExtensionsEndorsements
    third_party_details: ThirdPartyDetails
    intermediary_agent_details: IntermediaryAgentDetails
    intermediary_details: IntermediaryDetails
    other_insured_person_details: OtherInsuredPersonDetails
    premium_details_all: PremiumDetailsAll
    insured_person_premium_details: InsuredPersonPremiumDetails
    schedule_of_benefits: ScheduleOfBenefits
    policy_holder_policy_details: PolicyHolderPolicyDetails

class MedicalInsuranceResponse(BaseModel):
    medical_insurance: MedicalInsurance
