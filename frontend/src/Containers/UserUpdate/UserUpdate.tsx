import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Grid, TextField, MenuItem } from '@mui/material';
import * as userActions from '../../store/actionCreators/userActionCreators';
import { RootState } from '../../store/types';
import { UserDetails } from '../../types';
import { AppDispatch } from '../../store/store';


interface UserUpdateProps {
  onChange: (details: UserDetails) => void;
}

interface LanguageOption {
  value: string;
  label: string;
}

const languages: LanguageOption[] = [
  { value: "spanish", label: "Spanish" },
  { value: "english", label: "English" },
  { value: "tagalog", label: "Tagalog" },
];

const ethnicities = [
  'Hispanic',
  'Caucasian',
  'African American',
  'Asian',
  'Native American',
  'Alaska Native',
  'Native Hawaiian',
  'Pacific Islander',
  'Two or More Races',
  'Other'
] as const;

const states = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
] as const;

const initialUserDetails: UserDetails = {
  firstName: "",
  lastName: "",
  age: null,
  addressLine1: "",
  addressLine2: "",
  city: "",
  state: "",
  zipCode: "",
  country: "",
  phoneNumber: "",
  ethnicity: "",
  language: "english"
};

export const UserUpdate: React.FC<UserUpdateProps> = ({ onChange }) => {
  const dispatch = useDispatch<AppDispatch>();
  const user = useSelector((state: RootState) => state.user.user);
  const isLoggedIn = useSelector((state: RootState) => state.user.loggedIn);
  const isLoading = useSelector((state: RootState) => state.user.isLoading);
  const currentUserDetails = useSelector((state: RootState) => state.user.userDetails);
  const [userDetails, setUserDetails] = useState<UserDetails>(initialUserDetails);

  useEffect(() => {
    if (isLoggedIn && user?.email) {
      dispatch(userActions.getUserDetails());
    }
    return () => {
      setUserDetails(initialUserDetails);
    };
  }, []);

  useEffect(() => {
    if (!isLoading && currentUserDetails && Object.keys(currentUserDetails).length > 0) {
      setUserDetails(currentUserDetails as UserDetails);
    }
  }, [isLoading, currentUserDetails]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    const updatedUser = { ...userDetails, [name]: value };
    setUserDetails(updatedUser);
    onChange(updatedUser);
  };

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6}>
        <TextField
          label="First Name"
          name="firstName"
          value={userDetails.firstName}
          onChange={handleChange}
          fullWidth
        />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField
          label="Last Name"
          name="lastName"
          value={userDetails.lastName}
          onChange={handleChange}
          fullWidth
        />
      </Grid>
      <Grid item xs={12}>
        <TextField
          label="Age"
          name="age"
          type="number"
          value={userDetails.age ?? ''}
          onChange={handleChange}
          fullWidth
        />
      </Grid>
      <Grid item xs={12}>
        <TextField
          label="Address Line 1"
          name="addressLine1"
          value={userDetails.addressLine1}
          onChange={handleChange}
          fullWidth
        />
      </Grid>
      <Grid item xs={12}>
        <TextField
          label="Address Line 2"
          name="addressLine2"
          value={userDetails.addressLine2}
          onChange={handleChange}
          fullWidth
        />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField
          label="City"
          name="city"
          value={userDetails.city}
          onChange={handleChange}
          fullWidth
        />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField
          select
          label="State"
          name="state"
          value={userDetails.state}
          onChange={handleChange}
          fullWidth
        >
          <MenuItem value="">Select a state</MenuItem>
          {states.map((state) => (
            <MenuItem key={state} value={state}>
              {state}
            </MenuItem>
          ))}
        </TextField>
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField
          label="ZIP Code"
          name="zipCode"
          value={userDetails.zipCode}
          onChange={handleChange}
          fullWidth
        />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField
          label="Country"
          name="country"
          value={userDetails.country}
          onChange={handleChange}
          fullWidth
        />
      </Grid>
      <Grid item xs={12}>
        <TextField
          label="Phone Number"
          name="phoneNumber"
          value={userDetails.phoneNumber}
          onChange={handleChange}
          fullWidth
        />
      </Grid>
      <Grid item xs={12}>
        <TextField
          select
          label="Ethnicity"
          name="ethnicity"
          value={userDetails.ethnicity}
          onChange={handleChange}
          fullWidth
        >
          <MenuItem value="">Select ethnicity</MenuItem>
          {ethnicities.map((ethnicity) => (
            <MenuItem key={ethnicity} value={ethnicity}>
              {ethnicity}
            </MenuItem>
          ))}
        </TextField>
      </Grid>
      <Grid item xs={12}>
        <TextField
          select
          label="Preferred Language"
          name="language"
          value={userDetails.language}
          onChange={handleChange}
          fullWidth
        >
          {languages.map((language) => (
            <MenuItem key={language.value} value={language.value}>
              {language.label}
            </MenuItem>
          ))}
        </TextField>
      </Grid>
    </Grid>
  );
};

export default UserUpdate;
